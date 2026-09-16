import json
from typing import Any, AsyncIterator

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from agents.job_agent import build_agent

# Chat history lives in-memory and resets on backend restart. Application data
# (the actual job applications) is persisted separately in SQLite, so this only
# trades away conversation continuity across restarts, not data.
_checkpointer = InMemorySaver()
_agent = build_agent("You", checkpointer=_checkpointer)


def get_agent():
    return _agent


def _text_of(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


def _sse(event: str, data: dict) -> dict:
    return {"event": event, "data": json.dumps(data)}


async def _consume(agent, stream_input, thread_id: str) -> AsyncIterator[dict]:
    config = {"configurable": {"thread_id": thread_id}}
    try:
        async for chunk in agent.astream(stream_input, config, stream_mode=["messages", "updates"], version="v2"):
            if chunk["type"] == "messages":
                token, metadata = chunk["data"]
                if metadata.get("langgraph_node") == "model":
                    text = _text_of(getattr(token, "content", None))
                    if text:
                        yield _sse("token", {"text": text})
            elif chunk["type"] == "updates" and "__interrupt__" in chunk["data"]:
                for interrupt in chunk["data"]["__interrupt__"]:
                    yield _sse(
                        "interrupt",
                        {
                            "interrupt_id": interrupt.id,
                            "thread_id": thread_id,
                            "action_requests": interrupt.value["action_requests"],
                            "review_configs": interrupt.value["review_configs"],
                        },
                    )
                return
    except Exception as exc:  # surface to the client instead of a bare disconnect
        yield _sse("error", {"message": str(exc)})
        return
    yield _sse("done", {})


def stream_chat(message: str, thread_id: str) -> AsyncIterator[dict]:
    agent = get_agent()
    return _consume(agent, {"messages": [{"role": "user", "content": message}]}, thread_id)


def stream_resume(decisions: list[dict], thread_id: str) -> AsyncIterator[dict]:
    agent = get_agent()
    return _consume(agent, Command(resume={"decisions": decisions}), thread_id)


async def get_thread_state(thread_id: str) -> dict:
    agent = get_agent()
    config = {"configurable": {"thread_id": thread_id}}
    state = await agent.aget_state(config)
    messages = []
    for message in state.values.get("messages", []) if state.values else []:
        role = getattr(message, "type", "unknown")
        text = _text_of(getattr(message, "content", None))
        if text:
            messages.append({"role": role, "content": text})

    pending_interrupt = None
    if state.interrupts:
        interrupt = state.interrupts[0]
        pending_interrupt = {
            "interrupt_id": interrupt.id,
            "thread_id": thread_id,
            "action_requests": interrupt.value["action_requests"],
            "review_configs": interrupt.value["review_configs"],
        }

    return {"messages": messages, "pending_interrupt": pending_interrupt}

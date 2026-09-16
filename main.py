import os
import sys
import uuid

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.job_agent import build_agent
from app.db import init_db
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command


def _text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def make_print_stream(agent, config):
    def print_stream(chunks):
        for chunk in chunks:
            if chunk["type"] == "messages":
                token, metadata = chunk["data"]
                if metadata.get("langgraph_node") == "model":
                    text = _text_of(getattr(token, "content", None))
                    if text:
                        print(text, end="", flush=True)
            elif chunk["type"] == "updates":
                if "__interrupt__" in chunk["data"]:
                    for interrupt in chunk["data"]["__interrupt__"]:
                        decisions = []
                        for action in interrupt.value["action_requests"]:
                            print(f"\n⚠️  Approval needed: {action['description']}")
                            decision = input("Approve? (y/n): ").strip().lower()
                            if decision == "y":
                                decisions.append({"type": "approve"})
                            else:
                                reason = input("Reason for rejection (optional): ").strip()
                                # Note: HumanInTheLoopMiddleware uses `message` verbatim as the tool's
                                # result if provided, so a bare custom reason would replace (not add to)
                                # its default "tool was not executed" context — leaving the model
                                # unaware the action didn't happen. Always state that explicitly.
                                message = "The user rejected this action; the tool was NOT executed."
                                if reason:
                                    message += f" Reason given: {reason}"
                                decisions.append({"type": "reject", "message": message})
                        print_stream(
                            agent.stream(Command(resume={"decisions": decisions}), config, stream_mode=["messages", "updates"], version="v2")
                        )
        print()

    return print_stream


if __name__ == "__main__":
    init_db()
    username = input("Enter your name: ").strip() or "User"
    agent = build_agent(username, checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    print_stream = make_print_stream(agent, config)

    print(f"\n🗂️  Job Application Tracker — Welcome {username}!")
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        print("Assistant: ", end="")
        print_stream(agent.stream({"messages": [{"role": "user", "content": user_input}]}, config, stream_mode=["messages", "updates"], version="v2"))
        print()

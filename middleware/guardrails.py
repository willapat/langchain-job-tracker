from typing import Any
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langgraph.runtime import Runtime

class TopicGuardrail(AgentMiddleware):
    """Block requests that are not related to job tracking."""

    OFF_TOPIC_KEYWORDS = [
        "weather", "recipe", "cook", "sports", "movie", "music",
        "game", "news", "stock", "crypto", "dating", "travel"
    ]

    JOB_KEYWORDS = [
        "job", "apply", "application", "resume", "interview", "salary",
        "company", "role", "position", "career", "hire", "status",
        "delete", "update", "save", "show", "list", "what"
    ]

    @hook_config(can_jump_to=["end"])
    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        if not state["messages"]:
            return None

        last_message = state["messages"][-1]
        if last_message.type != "human":
            return None

        # Handle both string and list content
        content = last_message.content
        if isinstance(content, list):
            content = " ".join([block.get("text", "") if isinstance(block, dict) else str(block) for block in content])
        content = content.lower()

        if any(keyword in content for keyword in self.JOB_KEYWORDS):
            return None

        if any(keyword in content for keyword in self.OFF_TOPIC_KEYWORDS):
            return {
                "messages": [{
                    "role": "assistant",
                    "content": "I can only help with job application tracking. Try asking me to save a job, check your applications, or update a status."
                }],
                "jump_to": "end"
            }

        return None
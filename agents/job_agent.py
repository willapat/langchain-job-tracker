from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware, SummarizationMiddleware
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from langchain_core.runnables import RunnableConfig
import uuid
import sys
import os
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.job_tools import save_application, get_applications, update_status, delete_application, extract_and_save_job

load_dotenv()

# Ask for username once at startup
USERNAME = input("Enter your name: ").strip() or "User"

@dynamic_prompt
def personalized_prompt(request: ModelRequest) -> str:
    return f"""You are a job application tracking assistant for {USERNAME}.
Today's date is {date.today().strftime("%B %d, %Y")}.
Help the user manage their job applications by saving, retrieving, updating, and deleting applications.
When showing applications, format them in a clear readable way."""

tools = [save_application, get_applications, update_status, delete_application, extract_and_save_job]

agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=tools,
    middleware=[
        personalized_prompt,
        SummarizationMiddleware(
            model="google_genai:gemini-3.1-flash-lite",
            trigger=("messages", 20),
            keep=("messages", 10),
        ),
        HumanInTheLoopMiddleware(
            interrupt_on={
                "delete_application": True,
            }
        )
    ],
    checkpointer=InMemorySaver()
)

thread_id = str(uuid.uuid4())
config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

def print_stream(chunks):
    for chunk in chunks:
        if chunk["type"] == "messages":
            token, metadata = chunk["data"]
            if metadata.get("langgraph_node") == "model" and hasattr(token, "content"):
                content = token.content
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            print(block["text"], end="", flush=True)
                elif isinstance(content, str) and content:
                    print(content, end="", flush=True)
        elif chunk["type"] == "updates":
            if "__interrupt__" in chunk["data"]:
                for interrupt in chunk["data"]["__interrupt__"]:
                    for action in interrupt.value["action_requests"]:
                        print(f"\n⚠️  Approval needed: {action['description']}")
                        decision = input("Approve? (y/n): ").strip().lower()
                        if decision == "y":
                            resume_decision = {"type": "approve"}
                        else:
                            reason = input("Reason for rejection (optional): ").strip()
                            resume_decision = {"type": "reject", "message": reason or "User rejected the action."}
                        print_stream(agent.stream(
                            Command(resume={"decisions": [resume_decision]}),
                            config,
                            stream_mode="messages",
                            version="v2"
                        ))
    print()

def stream_chat(user_input: str):
    print_stream(agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode=["messages", "updates"],
        version="v2"
    ))

if __name__ == "__main__":
    print(f"\n🗂️  Job Application Tracker — Welcome {USERNAME}!")
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        print("Assistant: ", end="")
        stream_chat(user_input)
        print()
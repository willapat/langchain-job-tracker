import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.job_agent import create_job_tracker
from langgraph.checkpoint.memory import InMemorySaver

if __name__ == "__main__":
    username = input("Enter your name: ").strip() or "User"
    agent, stream_chat = create_job_tracker(username, checkpointer=InMemorySaver())

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
        stream_chat(user_input)
        print()
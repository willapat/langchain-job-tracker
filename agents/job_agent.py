import os
import sys
from datetime import date

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware, SummarizationMiddleware
from langchain.agents.middleware import dynamic_prompt, ModelRequest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.job_tools import (
    save_application,
    get_applications,
    update_status,
    delete_application,
    fetch_job_posting,
    extract_job_fields,
)
from middleware.guardrails import TopicGuardrail

load_dotenv()

MODEL = "google_genai:gemini-3.1-flash-lite"


def build_agent(username: str, checkpointer=None):
    """Build the job-tracker agent. Shared by the CLI (agents/job_agent.py -> main.py),
    the FastAPI backend (app/services/agent_runtime.py), and the langgraph dev server
    (langgraph.json points at the module-level `agent` below)."""

    @dynamic_prompt
    def personalized_prompt(request: ModelRequest) -> str:
        return f"""You are a job application tracking assistant for {username}.
Today's date is {date.today().strftime("%B %d, %Y")}.
Help the user manage their job applications by saving, retrieving, updating, and deleting applications.
When showing applications, format them in a clear readable way.

Adding a job from a link or pasted description is a common request and follows this workflow:
1. If given a URL, call fetch_job_posting to get its text. If that fails (e.g. a login wall),
   tell the user and ask them to paste the job description instead — don't guess at fields.
2. Call extract_job_fields on the text to get structured fields.
3. Review the result. If company or role is missing, or another important field (salary,
   location) is missing and the user might reasonably know it, ask a brief follow-up
   question before saving. For minor gaps, use your judgment — you don't need to interrogate
   the user over an unlisted salary.
4. Call save_application yourself once you're satisfied, passing source_url when you had one,
   then confirm to the user what was saved (and note anything left blank)."""

    tools = [save_application, get_applications, update_status, delete_application, fetch_job_posting, extract_job_fields]

    kwargs = dict(
        model=MODEL,
        tools=tools,
        middleware=[
            TopicGuardrail(),
            personalized_prompt,
            SummarizationMiddleware(
                model=MODEL,
                trigger=("messages", 20),
                keep=("messages", 10),
            ),
            HumanInTheLoopMiddleware(interrupt_on={"delete_application": True}),
        ],
    )

    if checkpointer is not None:
        kwargs["checkpointer"] = checkpointer

    return create_agent(**kwargs)


# For `langgraph dev` / LangGraph Studio — the platform manages its own checkpointer.
agent = build_agent("User")

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


class ExtractedJob(BaseModel):
    company: str = Field(description="The company name")
    role: str = Field(description="The job title or role")
    salary: str | None = Field(default=None, description="Salary or compensation if mentioned")
    location: str | None = Field(default=None, description="Job location or remote status")
    requirements: list[str] = Field(default_factory=list, description="Key requirements or qualifications")


def extract_job(text: str) -> ExtractedJob:
    """Turn raw job-posting text into structured fields via the LLM."""
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    structured_llm = llm.with_structured_output(ExtractedJob)
    return structured_llm.invoke(text)

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import Optional

load_dotenv()

# This is the schema - it defines exactly what shape the data comes out in
class JobApplication(BaseModel):
    company: str = Field(description="The company name")
    role: str = Field(description="The job title or role")
    salary: Optional[str] = Field(description="Salary or compensation if mentioned")
    location: Optional[str] = Field(description="Job location or remote status")
    requirements: list[str] = Field(description="Key requirements or qualifications")
    status: str = Field(default="applied", description="Application status")

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")

# This tells the model to return data matching your schema
structured_llm = llm.with_structured_output(JobApplication)

# Test it with a fake job description
test_description = """
Software Engineer at Acme Corp
Location: Remote
Salary: $120,000 - $140,000

We are looking for a software engineer with 2+ years of Python experience,
familiarity with REST APIs, and strong communication skills.
"""

result = structured_llm.invoke(test_description)
print(result)
print(type(result))
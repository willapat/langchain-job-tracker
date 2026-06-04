from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import Optional
import json
import os

# This is the same schema from before, tools will use this shape
class JobApplication(BaseModel):
    company: str = Field(description="The company name")
    role: str = Field(description="The job title or role")
    salary: Optional[str] = Field(description="Salary or compensation if mentioned")
    location: Optional[str] = Field(description="Job location or remote status")
    requirements: list[str] = Field(description="Key requirements or qualifications")
    status: str = Field(default="applied", description="Application status")

# We'll store jobs in a simple JSON file for now
JOBS_FILE = "jobs.json"

def load_jobs():
    if not os.path.exists(JOBS_FILE):
        return []
    with open(JOBS_FILE, "r") as f:
        return json.load(f)

def save_jobs(jobs):
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

@tool
def save_application(company: str, role: str, salary: Optional[str] = None, 
                     location: Optional[str] = None, requirements: list[str] = [], 
                     status: str = "applied") -> str:
    """Save a new job application to the tracker."""
    jobs = load_jobs()
    
    job = {
        "id": len(jobs) + 1,
        "company": company,
        "role": role,
        "salary": salary,
        "location": location,
        "requirements": requirements,
        "status": status
    }
    
    jobs.append(job)
    save_jobs(jobs)
    return f"Saved application for {role} at {company}"

@tool
def get_applications(status: Optional[str] = None) -> str:
    """Get all job applications, optionally filtered by status."""
    jobs = load_jobs()
    
    if status:
        jobs = [j for j in jobs if j["status"] == status]
    
    if not jobs:
        return "No applications found"
    
    return json.dumps(jobs, indent=2)

@tool
def update_status(company: str, new_status: str) -> str:
    """Update the status of a job application by company name."""
    jobs = load_jobs()
    
    for job in jobs:
        if job["company"].lower() == company.lower():
            job["status"] = new_status
            save_jobs(jobs)
            return f"Updated {company} status to {new_status}"
    
    return f"No application found for {company}"

@tool
def delete_application(company: str) -> str:
    """Delete a job application by company name."""
    jobs = load_jobs()
    original_len = len(jobs)
    jobs = [j for j in jobs if j["company"].lower() != company.lower()]
    
    if len(jobs) == original_len:
        return f"No application found for {company}"
    
    save_jobs(jobs)
    return f"Deleted application for {company}"

@tool
def extract_and_save_job(job_description: str) -> str:
    """Extract job details from a raw job description and save it automatically."""
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    structured_llm = llm.with_structured_output(JobApplication)
    
    job = structured_llm.invoke(job_description)
    
    jobs = load_jobs()
    job_dict = {
        "id": len(jobs) + 1,
        "company": job.company,
        "role": job.role,
        "salary": job.salary,
        "location": job.location,
        "requirements": job.requirements,
        "status": job.status
    }
    jobs.append(job_dict)
    save_jobs(jobs)
    
    return f"Extracted and saved: {job.role} at {job.company} | Salary: {job.salary} | Location: {job.location}"

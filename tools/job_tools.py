import json
from typing import Optional

from langchain_core.tools import tool

from app import crud
from app.db import session_scope
from app.services.extract import extract_job
from app.services.fetcher import FetchError, fetch_job_posting_text


def _format_application(app) -> dict:
    return {
        "id": app.id,
        "company": app.company,
        "role": app.role,
        "salary": app.salary,
        "location": app.location,
        "requirements": app.requirements,
        "status": app.status,
    }


@tool
def save_application(
    company: str,
    role: str,
    salary: Optional[str] = None,
    location: Optional[str] = None,
    requirements: Optional[list[str]] = None,
    status: str = "applied",
    source_url: Optional[str] = None,
) -> str:
    """Save a new job application to the tracker. Pass source_url when the application
    came from a job posting link, so the link is kept alongside the saved record."""
    with session_scope() as session:
        crud.create_application(
            session,
            company=company,
            role=role,
            salary=salary,
            location=location,
            requirements=requirements or [],
            status=status,
            source_url=source_url,
        )
    return f"Saved application for {role} at {company}"


@tool
def get_applications(status: Optional[str] = None) -> str:
    """Get all job applications, optionally filtered by status."""
    with session_scope() as session:
        applications = crud.list_applications(session, status=status)
        if not applications:
            return "No applications found"
        return json.dumps([_format_application(app) for app in applications], indent=2)


@tool
def update_status(company: str, new_status: str) -> str:
    """Update the status of a job application by company name."""
    with session_scope() as session:
        application = crud.update_status_by_company(session, company, new_status)
    if application is None:
        return f"No application found for {company}"
    return f"Updated {company} status to {new_status}"


@tool
def delete_application(company: str) -> str:
    """Delete a job application by company name."""
    with session_scope() as session:
        deleted = crud.delete_application_by_company(session, company)
    if not deleted:
        return f"No application found for {company}"
    return f"Deleted application for {company}"


@tool
def get_pipeline_stats() -> str:
    """Get aggregate stats about the user's job search: total applications, a count
    per status, response rate, and interview rate. Use this (instead of manually
    counting from get_applications) when asked for feedback or analysis of overall
    progress, so any numbers you cite are exact rather than estimated."""
    with session_scope() as session:
        return json.dumps(crud.get_stats(session), indent=2)


@tool
def fetch_job_posting(url: str) -> str:
    """Fetch a job posting URL and return its readable text, so it can be passed to
    extract_job_fields. If the page can't be read automatically (e.g. it requires a
    login, like many LinkedIn or Indeed postings), returns an error message explaining
    that — ask the user to paste the job description text instead in that case."""
    try:
        return fetch_job_posting_text(url)
    except FetchError as exc:
        return f"Could not read that page automatically: {exc.message}"


@tool
def extract_job_fields(job_description: str) -> str:
    """Extract structured job fields (company, role, salary, location, requirements)
    from raw job-posting text, WITHOUT saving anything. Review the result: if company
    or role is missing, or an important field like salary or location is missing and
    the user might know it, ask the user before calling save_application. Only call
    save_application yourself, once you're satisfied with the fields (asking the user
    is optional for minor gaps — use judgment)."""
    job = extract_job(job_description)
    return json.dumps(
        {
            "company": job.company,
            "role": job.role,
            "salary": job.salary,
            "location": job.location,
            "requirements": job.requirements,
        },
        indent=2,
    )

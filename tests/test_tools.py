import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.db as db


@pytest.fixture(autouse=True)
def temp_db(monkeypatch):
    from app import models  # noqa: F401  (register tables on Base.metadata)

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    db.Base.metadata.create_all(bind=engine)
    test_session_local = sessionmaker(bind=engine, expire_on_commit=False)
    monkeypatch.setattr(db, "SessionLocal", test_session_local)
    yield


def test_save_and_get_applications():
    from tools.job_tools import get_applications, save_application

    save_application.invoke({"company": "Spotify", "role": "Backend Engineer"})
    result = get_applications.invoke({})
    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["company"] == "Spotify"


def test_get_applications_empty_returns_message():
    from tools.job_tools import get_applications

    assert get_applications.invoke({}) == "No applications found"


def test_update_status_missing_company():
    from tools.job_tools import update_status

    result = update_status.invoke({"company": "Ghost Inc", "new_status": "interview"})
    assert "No application found" in result


def test_delete_application_round_trip():
    from tools.job_tools import delete_application, get_applications, save_application

    save_application.invoke({"company": "Stripe", "role": "Engineer"})
    result = delete_application.invoke({"company": "stripe"})
    assert "Deleted application" in result
    assert get_applications.invoke({}) == "No applications found"


def test_save_application_keeps_source_url():
    from tools.job_tools import get_applications, save_application

    save_application.invoke({"company": "Acme", "role": "Engineer", "source_url": "https://example.com/jobs/1"})
    data = json.loads(get_applications.invoke({}))
    assert data[0]["company"] == "Acme"


def test_extract_job_fields_does_not_save(monkeypatch):
    import tools.job_tools as job_tools
    from app.services.extract import ExtractedJob

    monkeypatch.setattr(
        job_tools,
        "extract_job",
        lambda text: ExtractedJob(company="Acme", role="Engineer", salary=None, location=None, requirements=[]),
    )
    result = job_tools.extract_job_fields.invoke({"job_description": "some posting text"})
    data = json.loads(result)
    assert data["company"] == "Acme"
    assert job_tools.get_applications.invoke({}) == "No applications found"


def test_fetch_job_posting_returns_error_message_on_blocked_url():
    from tools.job_tools import fetch_job_posting

    result = fetch_job_posting.invoke({"url": "http://169.254.169.254/latest/meta-data/"})
    assert "Could not read that page" in result

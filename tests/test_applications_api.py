import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.db as db


@pytest.fixture(autouse=True)
def temp_db(monkeypatch):
    from app import models  # noqa: F401

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    db.Base.metadata.create_all(bind=engine)
    test_session_local = sessionmaker(bind=engine, expire_on_commit=False)
    monkeypatch.setattr(db, "SessionLocal", test_session_local)
    yield


@pytest.fixture()
def client():
    from app.main import app

    return TestClient(app)


def test_create_application_via_api_with_default_fields(client):
    # Regression test: ApplicationCreate always sends `applied_date` (defaulting to
    # None) in its model_dump(), and the router forwards it verbatim to
    # crud.create_application — which previously didn't accept that kwarg at all,
    # so every plain POST /api/applications (e.g. the frontend's manual-add form)
    # returned a 500.
    resp = client.post("/api/applications", json={"company": "Acme", "role": "Engineer"})
    assert resp.status_code == 201
    assert resp.json()["company"] == "Acme"


def test_create_application_via_api_with_explicit_applied_date(client):
    resp = client.post(
        "/api/applications",
        json={"company": "Acme", "role": "Engineer", "applied_date": "2024-01-01"},
    )
    assert resp.status_code == 201
    assert resp.json()["applied_date"] == "2024-01-01"


def test_patch_application_status(client):
    created = client.post("/api/applications", json={"company": "Acme", "role": "Engineer"}).json()
    resp = client.patch(f"/api/applications/{created['id']}", json={"status": "interview"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "interview"

from app import crud


def test_create_and_list_application(session):
    crud.create_application(session, company="Spotify", role="Backend Engineer")
    apps = crud.list_applications(session)
    assert len(apps) == 1
    assert apps[0].company == "Spotify"
    assert apps[0].status == "applied"


def test_create_application_normalizes_status_casing(session):
    # Regression: the agent sometimes passes a differently-cased status (e.g.
    # "Applied"). The board matches status by exact string against its five
    # lowercase columns, so an un-normalized value saves successfully but
    # never renders anywhere — silently invisible, not an error.
    app = crud.create_application(session, company="Acme", role="Engineer", status="Applied")
    assert app.status == "applied"


def test_update_application_normalizes_status_casing(session):
    app = crud.create_application(session, company="Acme", role="Engineer")
    updated = crud.update_application(session, app.id, status="INTERVIEW")
    assert updated.status == "interview"


def test_update_status_by_company_normalizes_casing(session):
    crud.create_application(session, company="Acme", role="Engineer")
    updated = crud.update_status_by_company(session, "Acme", "Offer")
    assert updated.status == "offer"


def test_list_applications_filter_normalizes_casing(session):
    crud.create_application(session, company="Acme", role="Engineer", status="applied")
    assert len(crud.list_applications(session, status="Applied")) == 1


def test_create_application_with_explicit_applied_date(session):
    from datetime import date

    app = crud.create_application(session, company="Acme", role="Engineer", applied_date=date(2024, 1, 1))
    assert app.applied_date == date(2024, 1, 1)


def test_update_status_by_company_is_case_insensitive(session):
    crud.create_application(session, company="Spotify", role="Backend Engineer")
    updated = crud.update_status_by_company(session, "spotify", "interview")
    assert updated is not None
    assert updated.status == "interview"


def test_update_status_by_company_missing_returns_none(session):
    assert crud.update_status_by_company(session, "Nonexistent", "interview") is None


def test_delete_application_by_company(session):
    crud.create_application(session, company="Stripe", role="Engineer")
    assert crud.delete_application_by_company(session, "stripe") is True
    assert crud.list_applications(session) == []


def test_delete_application_by_company_missing(session):
    assert crud.delete_application_by_company(session, "Nonexistent") is False


def test_delete_application_cascades_notes(session):
    app = crud.create_application(session, company="Notion", role="Engineer")
    crud.add_note(session, app.id, "First note")
    assert crud.delete_application(session, app.id) is True
    session.flush()
    from app.models import Note

    assert session.get(Note, 1) is None


def test_add_note_to_missing_application_returns_none(session):
    assert crud.add_note(session, 999, "content") is None


def test_get_stats_empty(session):
    stats = crud.get_stats(session)
    assert stats["total"] == 0
    assert stats["response_rate"] == 0.0
    assert stats["interview_rate"] == 0.0


def test_get_stats_rates(session):
    crud.create_application(session, company="A", role="Eng", status="applied")
    crud.create_application(session, company="B", role="Eng", status="interview")
    crud.create_application(session, company="C", role="Eng", status="offer")
    crud.create_application(session, company="D", role="Eng", status="rejected")

    stats = crud.get_stats(session)
    assert stats["total"] == 4
    # responded: interview + offer = 2/4
    assert stats["response_rate"] == 0.5
    # interviewed: interview + offer = 2/4
    assert stats["interview_rate"] == 0.5

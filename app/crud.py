from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Application, Note

# ---- Applications ----------------------------------------------------------


def _normalize_status(status: str) -> str:
    """Statuses are matched by exact string against the board's five lowercase
    columns (applied/screening/interview/offer/rejected). Callers — including the
    agent, which sometimes passes "Applied" with a capital A — aren't guaranteed to
    send that exact casing, so normalize here rather than at every call site. A
    value that came in differently-cased would otherwise save successfully but
    silently match no column and never render anywhere on the board."""
    return status.strip().lower()


def list_applications(session: Session, status: str | None = None) -> list[Application]:
    stmt = select(Application).order_by(Application.created_at.desc())
    if status:
        stmt = stmt.where(Application.status == _normalize_status(status))
    return list(session.scalars(stmt))


def get_application(session: Session, application_id: int) -> Application | None:
    return session.get(Application, application_id)


def get_application_by_company(session: Session, company: str) -> Application | None:
    stmt = select(Application).where(func.lower(Application.company) == company.lower())
    return session.scalars(stmt).first()


def create_application(
    session: Session,
    *,
    company: str,
    role: str,
    salary: str | None = None,
    location: str | None = None,
    requirements: list[str] | None = None,
    status: str = "applied",
    source_url: str | None = None,
    applied_date: date | None = None,
) -> Application:
    application = Application(
        company=company,
        role=role,
        salary=salary,
        location=location,
        requirements=requirements or [],
        status=_normalize_status(status),
        source_url=source_url,
    )
    if applied_date is not None:
        application.applied_date = applied_date
    session.add(application)
    session.flush()
    session.refresh(application)
    return application


def update_application(session: Session, application_id: int, **fields) -> Application | None:
    application = session.get(Application, application_id)
    if application is None:
        return None
    for key, value in fields.items():
        if value is not None and hasattr(application, key):
            if key == "status":
                value = _normalize_status(value)
            setattr(application, key, value)
    session.flush()
    session.refresh(application)
    return application


def update_status_by_company(session: Session, company: str, new_status: str) -> Application | None:
    application = get_application_by_company(session, company)
    if application is None:
        return None
    application.status = _normalize_status(new_status)
    session.flush()
    session.refresh(application)
    return application


def delete_application(session: Session, application_id: int) -> bool:
    application = session.get(Application, application_id)
    if application is None:
        return False
    session.delete(application)
    return True


def delete_application_by_company(session: Session, company: str) -> bool:
    application = get_application_by_company(session, company)
    if application is None:
        return False
    session.delete(application)
    return True


# ---- Notes ------------------------------------------------------------------


def add_note(session: Session, application_id: int, content: str, kind: str = "note") -> Note | None:
    if session.get(Application, application_id) is None:
        return None
    note = Note(application_id=application_id, content=content, kind=kind)
    session.add(note)
    session.flush()
    session.refresh(note)
    return note


def update_note(session: Session, note_id: int, content: str) -> Note | None:
    note = session.get(Note, note_id)
    if note is None:
        return None
    note.content = content
    session.flush()
    session.refresh(note)
    return note


def delete_note(session: Session, note_id: int) -> bool:
    note = session.get(Note, note_id)
    if note is None:
        return False
    session.delete(note)
    return True


# ---- Stats -------------------------------------------------------------------


def get_stats(session: Session, days: int = 90) -> dict:
    total = session.scalar(select(func.count(Application.id))) or 0

    status_rows = session.execute(
        select(Application.status, func.count(Application.id)).group_by(Application.status)
    ).all()
    status_counts = {status: count for status, count in status_rows}

    since = date.today() - timedelta(days=days)
    time_rows = session.execute(
        select(Application.applied_date, func.count(Application.id))
        .where(Application.applied_date >= since)
        .group_by(Application.applied_date)
        .order_by(Application.applied_date)
    ).all()
    applied_over_time = [
        {"date": d.isoformat() if isinstance(d, date) else str(d), "count": c} for d, c in time_rows
    ]

    responded = sum(
        count for status, count in status_counts.items() if status in ("screening", "interview", "offer")
    )
    interviewed = sum(count for status, count in status_counts.items() if status in ("interview", "offer"))

    return {
        "total": total,
        "status_counts": status_counts,
        "applied_over_time": applied_over_time,
        "response_rate": round(responded / total, 3) if total else 0.0,
        "interview_rate": round(interviewed / total, 3) if total else 0.0,
    }

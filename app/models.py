from datetime import date, datetime, timezone

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    company: Mapped[str] = mapped_column(String(200), index=True)
    role: Mapped[str] = mapped_column(String(200))
    salary: Mapped[str | None] = mapped_column(String(120), default=None)
    location: Mapped[str | None] = mapped_column(String(200), default=None)
    requirements: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(40), default="applied", index=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), default=None)
    applied_date: Mapped[date] = mapped_column(default=lambda: datetime.now(timezone.utc).date())
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=_utcnow, onupdate=_utcnow)

    notes: Mapped[list["Note"]] = relationship(
        back_populates="application", cascade="all, delete-orphan", order_by="Note.created_at.desc()"
    )


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), index=True)
    content: Mapped[str] = mapped_column(String(4000))
    kind: Mapped[str] = mapped_column(String(40), default="note")  # "note" | "interview"
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)

    application: Mapped["Application"] = relationship(back_populates="notes")


STATUSES = ["applied", "screening", "interview", "offer", "rejected"]

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    content: str
    kind: str
    created_at: datetime


class NoteCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
    kind: str = Field(default="note", pattern="^(note|interview)$")


class NoteUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: str
    role: str
    salary: str | None
    location: str | None
    requirements: list[str]
    status: str
    source_url: str | None
    applied_date: date
    created_at: datetime
    updated_at: datetime
    notes: list[NoteOut] = []


class ApplicationCreate(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=200)
    salary: str | None = None
    location: str | None = None
    requirements: list[str] = []
    status: str = "applied"
    applied_date: date | None = None


class ApplicationUpdate(BaseModel):
    company: str | None = None
    role: str | None = None
    salary: str | None = None
    location: str | None = None
    requirements: list[str] | None = None
    status: str | None = None
    applied_date: date | None = None


class StatsOut(BaseModel):
    total: int
    status_counts: dict[str, int]
    applied_over_time: list[dict]
    response_rate: float
    interview_rate: float


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    thread_id: str = Field(min_length=1)


class ResumeDecision(BaseModel):
    type: str = Field(pattern="^(approve|reject|edit|respond)$")
    message: str | None = None


class ResumeRequest(BaseModel):
    thread_id: str = Field(min_length=1)
    decisions: list[ResumeDecision]

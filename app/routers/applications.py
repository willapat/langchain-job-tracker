from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.db import get_session
from app.schemas import ApplicationCreate, ApplicationOut, ApplicationUpdate, NoteCreate, NoteOut, NoteUpdate

router = APIRouter(prefix="/api/applications", tags=["applications"])
notes_router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.get("", response_model=list[ApplicationOut])
def list_applications(status: str | None = None, session: Session = Depends(get_session)):
    return crud.list_applications(session, status=status)


@router.post("", response_model=ApplicationOut, status_code=201)
def create_application(payload: ApplicationCreate, session: Session = Depends(get_session)):
    return crud.create_application(session, **payload.model_dump())


@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(application_id: int, session: Session = Depends(get_session)):
    application = crud.get_application(session, application_id)
    if application is None:
        raise HTTPException(404, "Application not found")
    return application


@router.patch("/{application_id}", response_model=ApplicationOut)
def update_application(application_id: int, payload: ApplicationUpdate, session: Session = Depends(get_session)):
    application = crud.update_application(session, application_id, **payload.model_dump(exclude_unset=True))
    if application is None:
        raise HTTPException(404, "Application not found")
    return application


@router.delete("/{application_id}", status_code=204)
def delete_application(application_id: int, session: Session = Depends(get_session)):
    if not crud.delete_application(session, application_id):
        raise HTTPException(404, "Application not found")


@router.get("/{application_id}/notes", response_model=list[NoteOut])
def list_notes(application_id: int, session: Session = Depends(get_session)):
    application = crud.get_application(session, application_id)
    if application is None:
        raise HTTPException(404, "Application not found")
    return application.notes


@router.post("/{application_id}/notes", response_model=NoteOut, status_code=201)
def create_note(application_id: int, payload: NoteCreate, session: Session = Depends(get_session)):
    note = crud.add_note(session, application_id, payload.content, payload.kind)
    if note is None:
        raise HTTPException(404, "Application not found")
    return note


@notes_router.patch("/{note_id}", response_model=NoteOut)
def update_note(note_id: int, payload: NoteUpdate, session: Session = Depends(get_session)):
    note = crud.update_note(session, note_id, payload.content)
    if note is None:
        raise HTTPException(404, "Note not found")
    return note


@notes_router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, session: Session = Depends(get_session)):
    if not crud.delete_note(session, note_id):
        raise HTTPException(404, "Note not found")

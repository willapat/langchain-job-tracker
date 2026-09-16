from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.db import get_session
from app.schemas import StatsOut

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=StatsOut)
def get_stats(session: Session = Depends(get_session)):
    return crud.get_stats(session)

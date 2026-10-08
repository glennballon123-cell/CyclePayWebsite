from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db_session
from app import schemas
from app.services import journal as journal_service

router = APIRouter(prefix="/api/journal", tags=["journal"])


@router.get("/", response_model=List[schemas.JournalEntryOut])
def list_entries(category: Optional[str] = None, q: str = "",
                 offset: int = 0, limit: int = 200,
                 db: Session = Depends(get_db_session)):
    return journal_service.list_filtered(db, category=category, query=q,
                                         offset=offset, limit=limit)


@router.post("/", response_model=schemas.JournalEntryOut, status_code=201)
def create_entry(payload: schemas.JournalEntryCreate, db: Session = Depends(get_db_session)):
    return journal_service.create(db, payload)


@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: int, db: Session = Depends(get_db_session)):
    if not journal_service.remove(db, entry_id):
        raise HTTPException(404, "Journal entry not found")


@router.get("/export")
def export_csv(category: Optional[str] = None, q: str = "",
               db: Session = Depends(get_db_session)):
    return {"csv": journal_service.export_csv(db, category=category, query=q)}
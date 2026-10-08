from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db_session
from app import schemas
from app.services import sessions as session_service

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("/account/{account_id}", response_model=List[schemas.LaundrySessionOut])
def list_for_account(account_id: int, db: Session = Depends(get_db_session)):
    return session_service.list_for_account(db, account_id)


@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: int, db: Session = Depends(get_db_session)):
    if not session_service.remove(db, session_id):
        raise HTTPException(404, "Session not found")
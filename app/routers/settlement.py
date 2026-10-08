from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db_session
from app import schemas
from app.services import settlement as settlement_service

router = APIRouter(prefix="/api/settlement", tags=["settlement"])


@router.post("/measure")
def measure(payload: schemas.MeasurementRequest, db: Session = Depends(get_db_session)):
    result = settlement_service.measure(db, payload)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.post("/issue")
def issue(payload: schemas.InstrumentIssueRequest, db: Session = Depends(get_db_session)):
    result = settlement_service.issue_instrument(db, payload)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.post("/consume")
def consume(payload: schemas.InstrumentConsumeRequest, db: Session = Depends(get_db_session)):
    result = settlement_service.consume_instrument(db, payload)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.post("/execute", response_model=schemas.SettlementResponse)
def execute(payload: schemas.SettlementRequest, db: Session = Depends(get_db_session)):
    result = settlement_service.execute_settlement(db, payload)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result
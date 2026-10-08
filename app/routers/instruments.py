from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db_session
from app import schemas
from app.codegen import sign_voucher_payload
from app.services import instruments as instrument_service
from app.services import settlement as settlement_service

router = APIRouter(prefix="/api/instruments", tags=["instruments"])


@router.get("/", response_model=List[schemas.InstrumentOut])
def list_instruments(db: Session = Depends(get_db_session)):
    return instrument_service.list_all(db)


@router.post("/issue", response_model=schemas.InstrumentIssueResponse, status_code=201)
def issue_instrument(payload: schemas.InstrumentIssueRequest,
                     db: Session = Depends(get_db_session)):
    instrument = instrument_service.issue(db, payload)
    signed = sign_voucher_payload(instrument.code)
    return {
        "id": instrument.id,
        "code": instrument.code,
        "value": instrument.value,
        "measured_kg": instrument.measured_kg,
        "station_number": instrument.station_number,
        "cycle_key": instrument.cycle_key,
        "signed_token": signed,
        "qr_payload": signed,
    }


@router.post("/consume")
def consume_instrument(payload: schemas.InstrumentConsumeRequest,
                       db: Session = Depends(get_db_session)):
    result = settlement_service.consume_instrument(db, payload)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.delete("/{instrument_id}", status_code=204)
def delete_instrument(instrument_id: int, db: Session = Depends(get_db_session)):
    if not instrument_service.remove(db, instrument_id):
        raise HTTPException(404, "Instrument not found")

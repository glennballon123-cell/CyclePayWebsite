from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db_session
from app import schemas
from app.services import equipment as equipment_service

router = APIRouter(prefix="/api/equipment", tags=["equipment"])


@router.get("/", response_model=List[schemas.EquipmentOut])
def list_equipment(db: Session = Depends(get_db_session)):
    return equipment_service.list_all(db)


@router.post("/", response_model=schemas.EquipmentOut, status_code=201)
def create_equipment(payload: schemas.EquipmentCreate, db: Session = Depends(get_db_session)):
    if equipment_service.fetch_by_station(db, payload.station_number):
        raise HTTPException(400, f"Station {payload.station_number} already exists")
    return equipment_service.create(db, payload)


@router.get("/{equipment_id}", response_model=schemas.EquipmentOut)
def show_equipment(equipment_id: int, db: Session = Depends(get_db_session)):
    entity = equipment_service.fetch(db, equipment_id)
    if not entity:
        raise HTTPException(404, "Equipment not found")
    return entity


@router.patch("/{equipment_id}", response_model=schemas.EquipmentOut)
def update_equipment(equipment_id: int, payload: schemas.EquipmentUpdate,
                     db: Session = Depends(get_db_session)):
    entity = equipment_service.modify(db, equipment_id, payload)
    if not entity:
        raise HTTPException(404, "Equipment not found")
    return entity


@router.delete("/{equipment_id}", status_code=204)
def delete_equipment(equipment_id: int, db: Session = Depends(get_db_session)):
    if not equipment_service.remove(db, equipment_id):
        raise HTTPException(404, "Equipment not found")
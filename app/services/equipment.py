from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app import models, schemas
from config.settings import hardware_settings


def create(db: Session, payload: schemas.EquipmentCreate) -> models.Equipment:
    entity = models.Equipment(
        station_number=payload.station_number,
        state=payload.state,
        load_kg=payload.load_kg,
        capacity_kg=payload.capacity_kg,
        firmware_label=hardware_settings.hardware_firmware_version,
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def fetch(db: Session, equipment_id: int) -> Optional[models.Equipment]:
    return db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()


def fetch_by_station(db: Session, station_number: int) -> Optional[models.Equipment]:
    return db.query(models.Equipment).filter(
        models.Equipment.station_number == station_number).first()


def list_all(db: Session) -> Sequence[models.Equipment]:
    return db.query(models.Equipment).order_by(models.Equipment.station_number).all()


def modify(db: Session, equipment_id: int, payload: schemas.EquipmentUpdate) -> Optional[models.Equipment]:
    entity = fetch(db, equipment_id)
    if not entity:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    db.commit()
    db.refresh(entity)
    return entity


def remove(db: Session, equipment_id: int) -> bool:
    entity = fetch(db, equipment_id)
    if not entity:
        return False
    db.delete(entity)
    db.commit()
    return True


def summarize(db: Session) -> dict:
    items = list_all(db)
    by_state = {state: 0 for state in models.EquipmentState}
    for unit in items:
        by_state[unit.state] += 1
    return {
        "total": len(items),
        "by_state": {state.value: count for state, count in by_state.items()},
        "sealed": sum(1 for u in items if u.is_sealed),
        "open": sum(1 for u in items if not u.is_sealed),
    }
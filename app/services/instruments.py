from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app import models, schemas
from app.codegen import build_instrument_code
from app.formatters import compute_duration, compute_price, resolve_cycle


def issue(db: Session, payload: schemas.InstrumentIssueRequest) -> models.Instrument:
    sequence = db.query(models.Instrument).count() + 1
    code = build_instrument_code(payload.station_number, sequence)
    price = compute_price(payload.measured_kg)
    entity = models.Instrument(
        code=code,
        value=price,
        measured_kg=payload.measured_kg,
        station_number=payload.station_number,
        cycle_key=payload.cycle_key,
        account_id=payload.account_id,
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def fetch_by_code(db: Session, code: str) -> Optional[models.Instrument]:
    return db.query(models.Instrument).filter(models.Instrument.code == code).first()


def list_all(db: Session) -> Sequence[models.Instrument]:
    return db.query(models.Instrument).order_by(models.Instrument.issued_at.desc()).all()


def consume(db: Session, code: str, account_id: int) -> models.Instrument:
    entity = fetch_by_code(db, code)
    if not entity or entity.is_consumed or not entity.is_active:
        raise ValueError("Instrument invalid or already consumed")
    if entity.account_id and entity.account_id != account_id:
        raise ValueError("Instrument does not belong to this account")

    equipment = db.query(models.Equipment).filter(
        models.Equipment.station_number == entity.station_number).first()
    if not equipment:
        raise ValueError("Target equipment not found")

    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise ValueError("Account not found")

    if account.balance < entity.value:
        raise ValueError("Insufficient balance")

    if not equipment.is_door_closed:
        raise ValueError("Load door must be closed before running")

    if abs(equipment.load_kg - entity.measured_kg) > 0.5:
        raise ValueError("Machine load does not match measured weight")

    account.balance -= entity.value
    entity.is_consumed = True
    entity.consumed_at = datetime.utcnow()

    cycle = resolve_cycle(entity.cycle_key)
    duration = compute_duration(entity.cycle_key, entity.measured_kg)

    equipment.state = models.EquipmentState.RUNNING
    equipment.is_sealed = True
    equipment.minutes_remaining = duration
    equipment.active_instrument_code = entity.code
    equipment.temperature_celsius = cycle["temperature_celsius"]
    equipment.rotation_rpm = cycle["rotation_rpm"]

    db.commit()
    db.refresh(entity)
    db.refresh(equipment)
    db.refresh(account)
    return entity


def remove(db: Session, instrument_id: int) -> bool:
    entity = db.query(models.Instrument).filter(models.Instrument.id == instrument_id).first()
    if not entity:
        return False
    db.delete(entity)
    db.commit()
    return True
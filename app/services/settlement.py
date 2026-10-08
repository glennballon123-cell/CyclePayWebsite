from sqlalchemy.orm import Session

from app import models, schemas
from app.codegen import build_integrity_hash, build_reference
from app.formatters import (
    compute_duration,
    compute_price,
    format_bay_label,
    resolve_cycle,
)
from app.services import equipment as equipment_service
from app.services import instruments as instrument_service
from app.services import journal as journal_service
from config.settings import hardware_settings


def measure(db: Session, payload: schemas.MeasurementRequest) -> dict:
    equipment = equipment_service.fetch_by_station(db, payload.station_number)
    if not equipment:
        return {"error": "Station not found"}
    if payload.measured_kg < hardware_settings.hardware_minimum_kg:
        return {"error": "Load below minimum threshold"}
    if payload.measured_kg > equipment.capacity_kg:
        return {"error": "Load exceeds station capacity"}

    price = compute_price(payload.measured_kg)
    equipment.load_kg = payload.measured_kg
    db.commit()
    db.refresh(equipment)

    journal_service.create(db, schemas.JournalEntryCreate(
        category=models.JournalCategory.MEASUREMENT,
        station_label=format_bay_label(equipment.station_number),
        description=f"Load measured at {payload.measured_kg:.2f} kg",
        actor_label="Weight Sensor",
        outcome=models.JournalOutcome.CALIBRATED,
        reference_code=build_reference("measurement", f"S{equipment.station_number:02d}"),
    ))

    return {
        "success": True,
        "station_number": payload.station_number,
        "measured_kg": payload.measured_kg,
        "price": price,
    }


def execute_settlement(db: Session, request: schemas.SettlementRequest) -> dict:
    equipment = equipment_service.fetch_by_station(db, request.station_number)
    if not equipment:
        return {"error": "Station not found"}

    if equipment.state not in (models.EquipmentState.AVAILABLE, models.EquipmentState.FINISHED):
        return {"error": f"Station is currently {equipment.state.value}"}

    account = db.query(models.Account).filter(models.Account.id == request.account_id).first() if request.account_id else None

    amount = compute_price(request.measured_kg)

    if request.method == models.SettlementMethod.BALANCE:
        if not account:
            return {"error": "Balance settlement requires an authenticated account"}
        if account.balance < amount:
            return {"error": "Insufficient balance"}
        account.balance -= amount

    issue_payload = schemas.InstrumentIssueRequest(
        station_number=request.station_number,
        measured_kg=request.measured_kg,
        cycle_key=request.cycle_key,
        account_id=account.id if account else None,
    )
    instrument = instrument_service.issue(db, issue_payload)
    cycle = resolve_cycle(request.cycle_key)
    duration = compute_duration(request.cycle_key, request.measured_kg)

    equipment.state = models.EquipmentState.RUNNING
    equipment.is_sealed = True
    equipment.is_door_closed = True
    equipment.load_kg = request.measured_kg
    equipment.minutes_remaining = duration
    equipment.active_instrument_code = instrument.code
    equipment.temperature_celsius = cycle["temperature_celsius"]
    equipment.rotation_rpm = cycle["rotation_rpm"]

    if account:
        db.add(models.LaundrySession(
            account_id=account.id,
            station_number=request.station_number,
            load_kg=request.measured_kg,
            cycle_label=cycle["label"],
            amount_paid=amount,
            method=request.method,
        ))

    journal_service.create(db, schemas.JournalEntryCreate(
        category=models.JournalCategory.SETTLEMENT,
        station_label=format_bay_label(request.station_number),
        description=f"Settlement {request.method.value} {amount:.2f}. Instrument {instrument.code}",
        actor_label=account.display_name if account else "Visitor",
        outcome=models.JournalOutcome.COMPLETED,
        reference_code=build_reference("settlement", instrument.code),
    ))

    db.commit()
    db.refresh(equipment)

    return {
        "success": True,
        "instrument_code": instrument.code,
        "station_number": request.station_number,
        "amount": amount,
        "balance_after": account.balance if account else None,
        "cycle_label": cycle["label"],
        "duration_minutes": duration,
    }


def consume_instrument(db: Session, payload: schemas.InstrumentConsumeRequest) -> dict:
    from app.codegen import verify_voucher_payload

    resolved_code = payload.code or ""
    if payload.signed_token:
        decoded = verify_voucher_payload(payload.signed_token, max_age_seconds=86400)
        if not decoded or "code" not in decoded:
            return {"error": "Voucher token is invalid or expired"}
        resolved_code = decoded["code"]

    if not resolved_code:
        return {"error": "No voucher code or token provided"}

    try:
        instrument = instrument_service.consume(db, resolved_code, payload.account_id)
    except ValueError as exc:
        return {"error": str(exc)}

    equipment = equipment_service.fetch_by_station(db, instrument.station_number)
    account = db.query(models.Account).filter(models.Account.id == payload.account_id).first()
    cycle = resolve_cycle(instrument.cycle_key)
    duration = compute_duration(instrument.cycle_key, instrument.measured_kg)

    equipment.minutes_remaining = duration
    db.commit()
    db.refresh(equipment)

    journal_service.create(db, schemas.JournalEntryCreate(
        category=models.JournalCategory.ACCESS,
        station_label=format_bay_label(instrument.station_number),
        description=f"Instrument {instrument.code} consumed. Cycle {cycle['label']} started",
        actor_label=account.display_name if account else "Visitor",
        outcome=models.JournalOutcome.CONFIRMED,
        reference_code=build_reference("access", instrument.code),
    ))

    if account:
        db.add(models.LaundrySession(
            account_id=account.id,
            station_number=instrument.station_number,
            load_kg=instrument.measured_kg,
            cycle_label=cycle["label"],
            amount_paid=instrument.value,
            method=models.SettlementMethod.INSTRUMENT,
        ))
        db.commit()

    return {
        "success": True,
        "instrument_code": instrument.code,
        "station_number": instrument.station_number,
        "cycle_label": cycle["label"],
        "duration_minutes": duration,
        "balance_after": account.balance if account else None,
    }
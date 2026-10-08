from app.database import Base, engine, SessionLocal
from app import models, schemas
from app.services import accounts as account_service
from app.services import equipment as equipment_service
from app.services import journal as journal_service
from config.facility import CYCLE_PROGRAMS
from config.settings import hardware_settings
from app.codegen import build_integrity_hash, build_reference
from app.formatters import format_bay_label


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if not equipment_service.list_all(db):
        initial = [
            (1, models.EquipmentState.AVAILABLE,    0.00, None, None, None, True,  False),
            (2, models.EquipmentState.RUNNING,      7.10, "LOP-020001", 42, 850, True,  True),
            (3, models.EquipmentState.EXTRACTING,   4.80, "LOP-030002", None, 1200, True, True),
            (4, models.EquipmentState.RUNNING,      5.20, "LOP-040003", 38, 780, True,  True),
            (5, models.EquipmentState.RUNNING,      6.40, "LOP-050004", 30, 600, True,  True),
            (6, models.EquipmentState.FINISHED,     5.82, None, None, None, True, True),
            (7, models.EquipmentState.AVAILABLE,    0.00, None, None, None, False, False),
            (8, models.EquipmentState.RUNNING,      8.12, "LOP-080005", 55, 780, True, True),
        ]
        for station, state, load, token, temp, rpm, sealed, door in initial:
            db.add(models.Equipment(
                station_number=station,
                state=state,
                load_kg=load,
                minutes_remaining=35 if state == models.EquipmentState.RUNNING else 0,
                active_instrument_code=token,
                temperature_celsius=temp,
                rotation_rpm=rpm,
                is_sealed=sealed,
                is_door_closed=door,
                capacity_kg=hardware_settings.hardware_max_load_kg,
                firmware_label=hardware_settings.hardware_firmware_version,
            ))
        db.commit()
        print(f"Seeded {len(initial)} equipment records")

    if not account_service.list_all(db):
        account_service.register(db, schemas.AccountCreate(
            display_name="Marcus Vance",
            contact_number="+639171234567",
            credential="1234",
            role=models.AccountRole.CLIENT,
            initial_balance=2450.00,
        ))
        account_service.register(db, schemas.AccountCreate(
            display_name="Admin-9481",
            contact_number="+639179481000",
            credential="admin",
            role=models.AccountRole.ADMIN,
            initial_balance=0.0,
        ))
        print("Seeded 2 accounts")

    if not journal_service.list_filtered(db):
        seed_entries = [
            (models.JournalCategory.SETTLEMENT,     7, "Counter settlement received", "Admin-9481", models.JournalOutcome.COMPLETED, "settlement"),
            (models.JournalCategory.ACCESS,         4, "Door released via instrument", "Marcus Vance", models.JournalOutcome.CONFIRMED, "access"),
            (models.JournalCategory.MEASUREMENT,    2, "Load cell calibration verified", "Sensor", models.JournalOutcome.CALIBRATED, "measurement"),
            (models.JournalCategory.ACCESS,         6, "Cycle complete; message dispatched", "System", models.JournalOutcome.NOTIFIED, "notification"),
            (models.JournalCategory.SETTLEMENT,     8, "Counter settlement received", "Admin-9481", models.JournalOutcome.COMPLETED, "settlement"),
            (models.JournalCategory.ADMINISTRATION, 0, "Admin authenticated", "Admin-9481", models.JournalOutcome.GRANTED, "administration"),
        ]
        for index, (category, station, description, actor, outcome, kind) in enumerate(seed_entries, start=1):
            code = f"SEED-{index:04d}"
            journal_service.create(db, schemas.JournalEntryCreate(
                category=category,
                station_label=format_bay_label(station) if station else "Control",
                description=description,
                actor_label=actor,
                outcome=outcome,
                reference_code=build_reference(kind, code),
                integrity_hash=build_integrity_hash(code),
            ))
        print(f"Seeded {len(seed_entries)} journal entries")

    client = account_service.fetch_by_contact(db, "+639171234567")
    if client and not db.query(models.LaundrySession).filter(
            models.LaundrySession.account_id == client.id).first():
        for station, load, cycle_key, amount in [
            (4, 5.20, "standard", 312.00),
            (2, 7.85, "heavy",    470.00),
            (6, 6.10, "drying",   366.00),
        ]:
            cycle = CYCLE_PROGRAMS[cycle_key]
            db.add(models.LaundrySession(
                account_id=client.id,
                station_number=station,
                load_kg=load,
                cycle_label=cycle["label"],
                amount_paid=amount,
                method=models.SettlementMethod.COUNTER,
            ))
        db.commit()
        print("Seeded 3 laundry sessions")

    db.close()
    print("\nDatabase seeded successfully.\n")


if __name__ == "__main__":
    seed()
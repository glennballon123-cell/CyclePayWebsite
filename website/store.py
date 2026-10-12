import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from itertools import count

DATA_FILE = os.environ.get("DATA_FILE", "laundry.json")


@dataclass
class Account:
    id: int
    display_name: str
    contact_number: str
    credential: str
    role: str
    balance: float
    created_at: str


@dataclass
class Equipment:
    id: int
    station_number: int
    state: str
    load_kg: float
    minutes_remaining: int
    active_instrument_code: str | None
    temperature_celsius: int | None
    rotation_rpm: int | None
    is_sealed: bool
    is_door_closed: bool
    capacity_kg: float
    firmware_label: str
    cycle_key: str


@dataclass
class Instrument:
    id: int
    code: str
    value: float
    measured_kg: float
    station_number: int
    cycle_key: str
    is_consumed: bool
    account_id: int | None


@dataclass
class JournalEntry:
    id: int
    occurred_at: str
    category: str
    station_label: str
    description: str
    actor_label: str
    outcome: str


@dataclass
class Session:
    id: int
    account_id: int
    station_number: int
    load_kg: float
    cycle_label: str
    amount_paid: float
    method: str
    started_at: str


class Store:
    def __init__(self):
        self.accounts = {}
        self.equipment = {}
        self.instruments = {}
        self.journal = {}
        self.sessions = {}
        self.ids = {k: count(1) for k in ("account", "equipment", "instrument", "journal", "session")}

    def next_id(self, kind):
        return next(self.ids[kind])

    def to_dict(self):
        return {
            "accounts": [asdict(a) for a in self.accounts.values()],
            "equipment": [asdict(e) for e in self.equipment.values()],
            "instruments": [asdict(i) for i in self.instruments.values()],
            "journal": [asdict(j) for j in self.journal.values()],
            "sessions": [asdict(s) for s in self.sessions.values()],
        }

    def load(self):
        if not os.path.exists(DATA_FILE):
            return False
        with open(DATA_FILE, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
        for row in raw.get("accounts", []):
            self.accounts[row["id"]] = Account(**row)
        for row in raw.get("equipment", []):
            row.setdefault("cycle_key", "standard")
            self.equipment[row["id"]] = Equipment(**row)
        for row in raw.get("instruments", []):
            self.instruments[row["id"]] = Instrument(**row)
        for row in raw.get("journal", []):
            self.journal[row["id"]] = JournalEntry(**row)
        for row in raw.get("sessions", []):
            self.sessions[row["id"]] = Session(**row)
        self.ids = {
            "account": count(max(self.accounts.keys(), default=0) + 1),
            "equipment": count(max(self.equipment.keys(), default=0) + 1),
            "instrument": count(max(self.instruments.keys(), default=0) + 1),
            "journal": count(max(self.journal.keys(), default=0) + 1),
            "session": count(max(self.sessions.keys(), default=0) + 1),
        }
        return True

    def save(self):
        folder = os.path.dirname(DATA_FILE)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, indent=2)


store = Store()


def persist():
    store.save()


def seed():
    if store.accounts:
        return
    create_account("Administrator", "09000000000", "admin123", "admin", 5000.0)
    for number in range(1, 5):
        create_equipment(number, "available", 0.0, 12.0)
    persist()


def create_account(display_name, contact_number, credential, role, balance):
    account = Account(id=store.next_id("account"), display_name=display_name, contact_number=contact_number, credential=credential, role=role, balance=balance, created_at=datetime.now().isoformat())
    store.accounts[account.id] = account
    return account


def find_account(account_id):
    return store.accounts.get(account_id)


def find_account_by_contact(contact_number):
    for account in store.accounts.values():
        if account.contact_number == contact_number:
            return account
    return None


def list_accounts():
    return sorted(store.accounts.values(), key=lambda a: a.id)


def update_account(account_id, **changes):
    account = store.accounts.get(account_id)
    if not account:
        return None
    for key, value in changes.items():
        setattr(account, key, value)
    return account


def delete_account(account_id):
    return store.accounts.pop(account_id, None)


def create_equipment(station_number, state, load_kg, capacity_kg):
    unit = Equipment(id=store.next_id("equipment"), station_number=station_number, state=state, load_kg=load_kg, minutes_remaining=0, active_instrument_code=None, temperature_celsius=None, rotation_rpm=None, is_sealed=False, is_door_closed=False, capacity_kg=capacity_kg, firmware_label="v1.0.0", cycle_key="standard")
    store.equipment[unit.id] = unit
    return unit


def find_equipment(equipment_id):
    return store.equipment.get(equipment_id)


def find_equipment_by_station(station_number):
    for unit in store.equipment.values():
        if unit.station_number == station_number:
            return unit
    return None


def list_equipment():
    return sorted(store.equipment.values(), key=lambda u: u.station_number)


def update_equipment(equipment_id, **changes):
    unit = store.equipment.get(equipment_id)
    if not unit:
        return None
    for key, value in changes.items():
        setattr(unit, key, value)
    return unit


def delete_equipment(equipment_id):
    return store.equipment.pop(equipment_id, None)


def create_instrument(code, value, measured_kg, station_number, cycle_key, account_id):
    instrument = Instrument(id=store.next_id("instrument"), code=code, value=value, measured_kg=measured_kg, station_number=station_number, cycle_key=cycle_key, is_consumed=False, account_id=account_id)
    store.instruments[instrument.id] = instrument
    return instrument


def find_instrument(instrument_id):
    return store.instruments.get(instrument_id)


def find_instrument_by_code(code):
    for instrument in store.instruments.values():
        if instrument.code == code:
            return instrument
    return None


def list_instruments():
    return sorted(store.instruments.values(), key=lambda i: i.id, reverse=True)


def delete_instrument(instrument_id):
    return store.instruments.pop(instrument_id, None)


def create_journal_entry(category, station_label, description, actor_label, outcome):
    entry = JournalEntry(id=store.next_id("journal"), occurred_at=datetime.now().isoformat(), category=category, station_label=station_label, description=description, actor_label=actor_label, outcome=outcome)
    store.journal[entry.id] = entry
    return entry


def list_journal(category=None, query=""):
    entries = sorted(store.journal.values(), key=lambda e: e.occurred_at, reverse=True)
    if category:
        entries = [e for e in entries if e.category == category]
    if query:
        needle = query.lower()
        entries = [e for e in entries if needle in e.description.lower() or needle in e.station_label.lower() or needle in e.actor_label.lower()]
    return entries


def delete_journal_entry(entry_id):
    return store.journal.pop(entry_id, None)


def create_session(account_id, station_number, load_kg, cycle_label, amount_paid, method):
    session = Session(id=store.next_id("session"), account_id=account_id, station_number=station_number, load_kg=load_kg, cycle_label=cycle_label, amount_paid=amount_paid, method=method, started_at=datetime.now().isoformat())
    store.sessions[session.id] = session
    return session


def list_sessions_for_account(account_id):
    return sorted((s for s in store.sessions.values() if s.account_id == account_id), key=lambda s: s.started_at, reverse=True)


def delete_session(session_id):
    return store.sessions.pop(session_id, None)
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models import (
    AccountRole, EquipmentState, JournalCategory,
    JournalOutcome, SettlementMethod,
)


class AccountCreate(BaseModel):
    display_name: str
    contact_number: str
    credential: str
    role: AccountRole = AccountRole.CLIENT
    initial_balance: float = 0.0


class AccountUpdate(BaseModel):
    display_name: Optional[str] = None
    balance: Optional[float] = None
    notify_by_message: Optional[bool] = None
    notify_by_sound: Optional[bool] = None


class AccountOut(BaseModel):
    id: int
    display_name: str
    contact_number: str
    role: AccountRole
    balance: float
    notify_by_message: bool
    notify_by_sound: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EquipmentCreate(BaseModel):
    station_number: int
    state: EquipmentState = EquipmentState.AVAILABLE
    load_kg: float = 0.0
    capacity_kg: float = Field(default=12.0, gt=0)


class EquipmentUpdate(BaseModel):
    state: Optional[EquipmentState] = None
    load_kg: Optional[float] = None
    minutes_remaining: Optional[int] = None
    active_instrument_code: Optional[str] = None
    temperature_celsius: Optional[int] = None
    rotation_rpm: Optional[int] = None
    is_sealed: Optional[bool] = None
    is_door_closed: Optional[bool] = None


class EquipmentOut(BaseModel):
    id: int
    station_number: int
    state: EquipmentState
    load_kg: float
    minutes_remaining: int
    active_instrument_code: Optional[str]
    temperature_celsius: Optional[int]
    rotation_rpm: Optional[int]
    is_sealed: bool
    is_door_closed: bool
    capacity_kg: float
    firmware_label: Optional[str]

    class Config:
        from_attributes = True


class MeasurementRequest(BaseModel):
    station_number: int
    measured_kg: float = Field(gt=0)


class InstrumentIssueRequest(BaseModel):
    station_number: int
    measured_kg: float = Field(gt=0)
    cycle_key: str = "standard"
    account_id: Optional[int] = None


class InstrumentConsumeRequest(BaseModel):
    code: str
    account_id: int


class InstrumentOut(BaseModel):
    id: int
    code: str
    value: float
    measured_kg: float
    station_number: int
    cycle_key: str
    is_active: bool
    is_consumed: bool
    account_id: Optional[int]
    issued_at: datetime
    consumed_at: Optional[datetime]
    signed_token: Optional[str] = None

    class Config:
        from_attributes = True


class InstrumentIssueResponse(BaseModel):
    id: int
    code: str
    value: float
    measured_kg: float
    station_number: int
    cycle_key: str
    signed_token: str
    qr_payload: str

    class Config:
        from_attributes = True


class InstrumentConsumeRequest(BaseModel):
    code: str = ""
    account_id: int
    signed_token: Optional[str] = None

class JournalEntryCreate(BaseModel):
    category: JournalCategory
    station_label: str
    description: str
    actor_label: str
    outcome: JournalOutcome
    reference_code: str
    integrity_hash: str = ""


class JournalEntryOut(BaseModel):
    id: int
    occurred_at: datetime
    category: JournalCategory
    station_label: str
    description: str
    actor_label: str
    outcome: JournalOutcome
    reference_code: str
    integrity_hash: str

    class Config:
        from_attributes = True


class LaundrySessionOut(BaseModel):
    id: int
    account_id: int
    station_number: int
    load_kg: float
    cycle_label: str
    amount_paid: float
    method: SettlementMethod
    started_at: datetime

    class Config:
        from_attributes = True


class SettlementRequest(BaseModel):
    station_number: int
    measured_kg: float = Field(gt=0)
    cycle_key: str = "standard"
    method: SettlementMethod = SettlementMethod.BALANCE
    account_id: Optional[int] = None


class SettlementResponse(BaseModel):
    success: bool
    instrument_code: str
    station_number: int
    amount: float
    balance_after: Optional[float]
    cycle_label: str
    duration_minutes: int

class InstrumentIssueResponse(BaseModel):
    id: int
    code: str
    value: float
    measured_kg: float
    station_number: int
    cycle_key: str
    signed_token: str
    qr_payload: str

    class Config:
        from_attributes = True


class InstrumentConsumeRequest(BaseModel):
    code: str = ""
    account_id: int
    signed_token: Optional[str] = None

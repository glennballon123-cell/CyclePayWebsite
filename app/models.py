from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SqlEnum, Float,
    ForeignKey, Integer, String, Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class EquipmentState(str, PyEnum):
    AVAILABLE = "available"
    RUNNING = "running"
    EXTRACTING = "extracting"
    FINISHED = "finished"
    OUT_OF_SERVICE = "out_of_service"


class JournalCategory(str, PyEnum):
    SETTLEMENT = "settlement"
    ACCESS = "access"
    MEASUREMENT = "measurement"
    ADMINISTRATION = "administration"


class JournalOutcome(str, PyEnum):
    COMPLETED = "completed"
    CONFIRMED = "confirmed"
    CALIBRATED = "calibrated"
    NOTIFIED = "notified"
    SEALED = "sealed"
    GRANTED = "granted"
    REJECTED = "rejected"


class AccountRole(str, PyEnum):
    CLIENT = "client"
    ADMIN = "admin"
    VISITOR = "visitor"


class SettlementMethod(str, PyEnum):
    COUNTER = "counter"
    INSTRUMENT = "instrument"
    BALANCE = "balance"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    display_name = Column(String(120), nullable=False)
    contact_number = Column(String(20), unique=True, nullable=False, index=True)
    credential_hash = Column(String(255), nullable=False)
    role = Column(SqlEnum(AccountRole), default=AccountRole.CLIENT, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    notify_by_message = Column(Boolean, default=True)
    notify_by_sound = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    instruments = relationship("Instrument", back_populates="account", cascade="all, delete-orphan")
    sessions = relationship("LaundrySession", back_populates="account", cascade="all, delete-orphan")


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    station_number = Column(Integer, unique=True, nullable=False, index=True)
    state = Column(SqlEnum(EquipmentState), default=EquipmentState.AVAILABLE, nullable=False)
    load_kg = Column(Float, default=0.0)
    minutes_remaining = Column(Integer, default=0)
    active_instrument_code = Column(String(40), nullable=True)
    temperature_celsius = Column(Integer, nullable=True)
    rotation_rpm = Column(Integer, nullable=True)
    is_sealed = Column(Boolean, default=True)
    is_door_closed = Column(Boolean, default=False)
    capacity_kg = Column(Float, nullable=False)
    firmware_label = Column(String(40), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(40), unique=True, nullable=False, index=True)
    value = Column(Float, nullable=False)
    measured_kg = Column(Float, nullable=False)
    station_number = Column(Integer, nullable=False)
    cycle_key = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    is_consumed = Column(Boolean, default=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    issued_at = Column(DateTime, default=datetime.utcnow)
    consumed_at = Column(DateTime, nullable=True)

    account = relationship("Account", back_populates="instruments")


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    occurred_at = Column(DateTime, default=datetime.utcnow, index=True)
    category = Column(SqlEnum(JournalCategory), nullable=False, index=True)
    station_label = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    actor_label = Column(String(120), nullable=False)
    outcome = Column(SqlEnum(JournalOutcome), nullable=False)
    reference_code = Column(String(40), nullable=False)
    integrity_hash = Column(String(80), nullable=False)


class LaundrySession(Base):
    __tablename__ = "laundry_sessions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    station_number = Column(Integer, nullable=False)
    load_kg = Column(Float, nullable=False)
    cycle_label = Column(String(80), nullable=False)
    amount_paid = Column(Float, nullable=False)
    method = Column(SqlEnum(SettlementMethod), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)

    account = relationship("Account", back_populates="sessions")
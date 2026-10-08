from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app import models, schemas
from app.security import hash_credential, verify_credential


def register(db: Session, payload: schemas.AccountCreate) -> models.Account:
    existing = db.query(models.Account).filter(
        models.Account.contact_number == payload.contact_number).first()
    if existing:
        raise ValueError("Contact number already registered")
    if payload.role == models.AccountRole.ADMIN:
        existing_admin = db.query(models.Account).filter(
            models.Account.role == models.AccountRole.ADMIN).first()
        if existing_admin:
            raise ValueError("An admin account already exists")
    entity = models.Account(
        display_name=payload.display_name,
        contact_number=payload.contact_number,
        credential_hash=hash_credential(payload.credential),
        role=payload.role,
        balance=payload.initial_balance,
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def fetch(db: Session, account_id: int) -> Optional[models.Account]:
    return db.query(models.Account).filter(models.Account.id == account_id).first()


def fetch_by_contact(db: Session, contact: str) -> Optional[models.Account]:
    return db.query(models.Account).filter(models.Account.contact_number == contact).first()


def list_all(db: Session) -> Sequence[models.Account]:
    return db.query(models.Account).order_by(models.Account.id).all()


def modify(db: Session, account_id: int, payload: schemas.AccountUpdate) -> Optional[models.Account]:
    entity = fetch(db, account_id)
    if not entity:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    db.commit()
    db.refresh(entity)
    return entity


def remove(db: Session, account_id: int) -> bool:
    entity = fetch(db, account_id)
    if not entity:
        return False
    db.delete(entity)
    db.commit()
    return True


def authenticate(db: Session, contact: str, credential: str) -> Optional[models.Account]:
    entity = fetch_by_contact(db, contact)
    if not entity:
        return None
    if not verify_credential(credential, entity.credential_hash):
        return None
    return entity


def credit(db: Session, account_id: int, amount: float) -> dict:
    entity = fetch(db, account_id)
    if not entity:
        return {"error": "Account not found"}
    if amount == 0:
        return {"error": "Amount cannot be zero"}
    entity.balance += amount
    if entity.balance < 0:
        entity.balance = 0
    db.commit()
    db.refresh(entity)
    return {"success": True, "balance": entity.balance}


def set_balance(db: Session, account_id: int, amount: float) -> dict:
    entity = fetch(db, account_id)
    if not entity:
        return {"error": "Account not found"}
    if amount < 0:
        return {"error": "Balance cannot be negative"}
    entity.balance = amount
    db.commit()
    db.refresh(entity)
    return {"success": True, "balance": entity.balance}

def set_balance(db: Session, account_id: int, amount: float) -> dict:
    entity = fetch(db, account_id)
    if not entity:
        return {"error": "Account not found"}
    if amount < 0:
        return {"error": "Balance cannot be negative"}
    entity.balance = amount
    db.commit()
    db.refresh(entity)
    return {"success": True, "balance": entity.balance}

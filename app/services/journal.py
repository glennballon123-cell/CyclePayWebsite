from typing import Optional, Sequence

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas
from app.codegen import build_integrity_hash


def create(db: Session, payload: schemas.JournalEntryCreate) -> models.JournalEntry:
    if not payload.integrity_hash:
        payload.integrity_hash = build_integrity_hash(payload.reference_code)
    entity = models.JournalEntry(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def list_filtered(
    db: Session,
    category: Optional[str] = None,
    query: str = "",
    offset: int = 0,
    limit: int = 200,
) -> Sequence[models.JournalEntry]:
    statement = db.query(models.JournalEntry)
    if category:
        statement = statement.filter(models.JournalEntry.category == category)
    if query:
        pattern = f"%{query}%"
        statement = statement.filter(or_(
            models.JournalEntry.description.ilike(pattern),
            models.JournalEntry.station_label.ilike(pattern),
            models.JournalEntry.actor_label.ilike(pattern),
        ))
    return (statement
            .order_by(models.JournalEntry.occurred_at.desc())
            .offset(offset).limit(limit).all())


def remove(db: Session, entry_id: int) -> bool:
    entity = db.query(models.JournalEntry).filter(models.JournalEntry.id == entry_id).first()
    if not entity:
        return False
    db.delete(entity)
    db.commit()
    return True


def export_csv(db: Session, category: Optional[str] = None, query: str = "") -> str:
    rows = ["occurred_at,category,station,description,actor,outcome,reference"]
    for entry in list_filtered(db, category=category, query=query, limit=10000):
        rows.append(
            f"{entry.occurred_at.isoformat()},{entry.category.value},"
            f"{entry.station_label},\"{entry.description}\",{entry.actor_label},"
            f"{entry.outcome.value},{entry.reference_code}"
        )
    return "\n".join(rows)
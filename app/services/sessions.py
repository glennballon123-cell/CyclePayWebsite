from typing import Sequence

from sqlalchemy.orm import Session

from app import models


def list_for_account(db: Session, account_id: int) -> Sequence[models.LaundrySession]:
    return (db.query(models.LaundrySession)
            .filter(models.LaundrySession.account_id == account_id)
            .order_by(models.LaundrySession.started_at.desc())
            .all())


def remove(db: Session, session_id: int) -> bool:
    entity = db.query(models.LaundrySession).filter(models.LaundrySession.id == session_id).first()
    if not entity:
        return False
    db.delete(entity)
    db.commit()
    return True
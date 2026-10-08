from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.models import Account, AccountRole
from app.security import parse_session_token
from config.settings import app_settings


def current_account(
    db: Session = Depends(get_db_session),
    session_token: Optional[str] = Cookie(default=None, alias=app_settings.session_cookie),
):
    if not session_token:
        return None
    payload = parse_session_token(session_token)
    account_id = payload.get("account_id")
    if not account_id:
        return None
    return db.query(Account).filter(Account.id == account_id).first()


def authenticated_account(account=Depends(current_account)):
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return account


def admin_account(account=Depends(current_account)):
    if not account or account.role != AccountRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return account
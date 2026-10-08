from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db_session
from app import schemas
from app.dependencies import current_account
from app.models import AccountRole
from app.security import issue_session_token
from app.services import accounts as account_service
from config.settings import app_settings

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("/", response_model=List[schemas.AccountOut])
def list_accounts(db: Session = Depends(get_db_session)):
    return account_service.list_all(db)


@router.post("/", response_model=schemas.AccountOut, status_code=201)
def create_account(payload: schemas.AccountCreate, db: Session = Depends(get_db_session)):
    try:
        return account_service.register(db, payload)
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@router.get("/{account_id}", response_model=schemas.AccountOut)
def show_account(account_id: int, db: Session = Depends(get_db_session)):
    entity = account_service.fetch(db, account_id)
    if not entity:
        raise HTTPException(404, "Account not found")
    return entity


@router.patch("/{account_id}", response_model=schemas.AccountOut)
def update_account(account_id: int, payload: schemas.AccountUpdate,
                   db: Session = Depends(get_db_session)):
    entity = account_service.modify(db, account_id, payload)
    if not entity:
        raise HTTPException(404, "Account not found")
    return entity


@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db_session)):
    if not account_service.remove(db, account_id):
        raise HTTPException(404, "Account not found")


@router.post("/authenticate")
def authenticate(
    contact: str,
    credential: str,
    role: str = "client",
    response: Response = None,
    db: Session = Depends(get_db_session),
):
    if role not in ("client", "admin"):
        raise HTTPException(400, "Invalid role")

    entity = account_service.authenticate(db, contact, credential)
    if not entity:
        raise HTTPException(401, "Invalid credentials")

    if role == "client" and entity.role != AccountRole.CLIENT:
        raise HTTPException(401, "Invalid credentials")

    if role == "admin" and entity.role != AccountRole.ADMIN:
        raise HTTPException(401, "Invalid credentials")

    token = issue_session_token(entity.id)
    response.set_cookie(
        key=app_settings.session_cookie,
        value=token,
        max_age=app_settings.session_max_age_seconds,
        httponly=True, samesite="lax",
    )
    return {"success": True, "account": schemas.AccountOut.model_validate(entity)}


@router.post("/deauthenticate")
def deauthenticate(response: Response):
    response.delete_cookie(app_settings.session_cookie)
    return {"success": True}


@router.get("/me", response_model=Optional[schemas.AccountOut])
def me(account=Depends(current_account)):
    return account


@router.post("/{account_id}/credit")
def credit_account(account_id: int, amount: float, db: Session = Depends(get_db_session)):
    result = account_service.credit(db, account_id, amount)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result

@router.post("/{account_id}/balance")
def set_balance_route(account_id: int, amount: float, db: Session = Depends(get_db_session)):
    result = account_service.set_balance(db, account_id, amount)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result

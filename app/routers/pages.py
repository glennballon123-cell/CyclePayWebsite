from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.models import EquipmentState
from app.database import get_db_session
from app.dependencies import current_account
from app.models import AccountRole, EquipmentState
from app.services import accounts as account_service
from app.services import equipment as equipment_service
from app.services import instruments as instrument_service
from app.services import journal as journal_service
from app.services import sessions as session_service
from app.formatters import (
    compute_imperial_pounds, compute_price, format_bay_label,
    format_capacity_percentage, format_currency, format_duration,
    format_load, format_rotation, format_station, format_state_label,
    format_temperature, resolve_cycle,
)
from config.facility import CYCLE_PROGRAMS

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


def build_context(request: Request, account, active: str, **extra) -> dict:
    context = {
        "request": request,
        "account": account,
        "active": active,
        "format_currency": format_currency,
        "format_station": format_station,
        "format_bay_label": format_bay_label,
        "format_state_label": format_state_label,
        "format_duration": format_duration,
        "format_temperature": format_temperature,
        "format_rotation": format_rotation,
        "format_load": format_load,
        "format_capacity_percentage": format_capacity_percentage,
        "compute_imperial_pounds": compute_imperial_pounds,
        "compute_price": compute_price,
        "resolve_cycle": resolve_cycle,
        "cycle_programs": CYCLE_PROGRAMS,
    }
    context.update(extra)
    return context


def is_admin(account) -> bool:
    return account is not None and account.role == AccountRole.ADMIN


@router.get("/", response_class=HTMLResponse)
def root(request: Request, db: Session = Depends(get_db_session),
         account=Depends(current_account)):
    return templates.TemplateResponse("landing.html",
                                      build_context(request, account, "landing"))


@router.get("/access", response_class=HTMLResponse)
def access_page(request: Request, account=Depends(current_account)):
    return templates.TemplateResponse("access.html",
                                      build_context(request, account, "access"))


@router.get("/overview", response_class=HTMLResponse)
def overview_page(request: Request, db: Session = Depends(get_db_session),
                  account=Depends(current_account)):
    if not is_admin(account):
        return RedirectResponse("/access")
    units = equipment_service.list_all(db)
    entries = journal_service.list_filtered(db, limit=20)
    summary = equipment_service.summarize(db)
    return templates.TemplateResponse("overview.html",
                                      build_context(request, account, "overview",
                                                    units=units, entries=entries,
                                                    summary=summary))


@router.get("/equipment", response_class=HTMLResponse)
def equipment_page(request: Request, db: Session = Depends(get_db_session),
                   account=Depends(current_account)):
    if not is_admin(account):
        return RedirectResponse("/access")
    units = equipment_service.list_all(db)
    summary = equipment_service.summarize(db)
    instruments = instrument_service.list_all(db)
    accounts = account_service.list_all(db)
    return templates.TemplateResponse("equipment.html",
                                      build_context(request, account, "equipment",
                                                    units=units, summary=summary,
                                                    instruments=instruments,
                                                    accounts=accounts))


@router.get("/journal", response_class=HTMLResponse)
def journal_page(request: Request, category: str = "", q: str = "",
                 db: Session = Depends(get_db_session),
                 account=Depends(current_account)):
    if not is_admin(account):
        return RedirectResponse("/access")
    entries = journal_service.list_filtered(db, category=category or None, query=q)
    return templates.TemplateResponse("journal.html",
                                      build_context(request, account, "journal",
                                                    entries=entries,
                                                    active_category=category,
                                                    search_term=q))


@router.get("/kiosk", response_class=HTMLResponse)
def kiosk_page(request: Request, db: Session = Depends(get_db_session),
               account=Depends(current_account)):
    units = equipment_service.list_all(db)
    return templates.TemplateResponse("kiosk.html",
                                      build_context(request, account, "kiosk", units=units))


@router.get("/wallet", response_class=HTMLResponse)
def wallet_page(request: Request, db: Session = Depends(get_db_session),
                account=Depends(current_account)):
    if not account:
        return RedirectResponse("/access")
    trips = session_service.list_for_account(db, account.id)
    units = equipment_service.list_all(db)
    return templates.TemplateResponse("wallet.html",
                                      build_context(request, account, "wallet",
                                                    trips=trips, units=units))


@router.get("/progress", response_class=HTMLResponse)
def progress_page(request: Request, db: Session = Depends(get_db_session),
                  account=Depends(current_account)):
    unit = None
    latest_session = None

    if account:
        sessions = session_service.list_for_account(db, account.id)
        if sessions:
            latest_session = sessions[0]
            unit = equipment_service.fetch_by_station(db, latest_session.station_number)

    if not unit:
        running = [u for u in equipment_service.list_all(db)
                   if u.state == EquipmentState.RUNNING]
        if running:
            unit = running[0]

    if not unit:
        all_units = equipment_service.list_all(db)
        unit = all_units[0] if all_units else None

    session_started_iso = ""
    if latest_session:
        session_started_iso = latest_session.started_at.isoformat()

    return templates.TemplateResponse("progress.html",
                                      build_context(request, account, "progress",
                                                    unit=unit,
                                                    latest_session=latest_session,
                                                    session_started_iso=session_started_iso))

@router.get("/help", response_class=HTMLResponse)
def help_page(request: Request, account=Depends(current_account)):
    return templates.TemplateResponse("help.html",
                                      build_context(request, account, "help"))


@router.get("/guide", response_class=HTMLResponse)
def guide_page(request: Request, account=Depends(current_account)):
    return templates.TemplateResponse("guide.html",
                                      build_context(request, account, "guide"))


@router.get("/policy", response_class=HTMLResponse)
def policy_page(request: Request, account=Depends(current_account)):
    return templates.TemplateResponse("policy.html",
                                      build_context(request, account, "policy"))
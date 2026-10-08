from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import (
    accounts, equipment, instruments, journal, pages,
    sessions, settlement,
)
from app.routers.pages import templates
from config.settings import app_settings, facility_settings, hardware_settings


def create_application() -> FastAPI:
    application = FastAPI(title=facility_settings.facility_name)

    Base.metadata.create_all(bind=engine)

    application.mount("/static", StaticFiles(directory="app/static"), name="static")

    application.include_router(pages.router)
    application.include_router(equipment.router)
    application.include_router(accounts.router)
    application.include_router(instruments.router)
    application.include_router(journal.router)
    application.include_router(sessions.router)
    application.include_router(settlement.router)

    templates.env.globals.update(
        facility_name=facility_settings.facility_name,
        facility_short_code=facility_settings.facility_short_code,
        facility_location=facility_settings.facility_location,
        facility_hotline=facility_settings.facility_hotline,
        facility_support_email=facility_settings.facility_support_email,
        facility_currency=facility_settings.facility_currency_symbol,
        hardware_firmware=hardware_settings.hardware_firmware_version,
        hardware_price_per_kg=hardware_settings.hardware_price_per_kg,
        hardware_minimum_kg=hardware_settings.hardware_minimum_kg,
        hardware_max_load_kg=hardware_settings.hardware_max_load_kg,
    )

    @application.get("/health")
    def health():
        return {
            "status": "ok",
            "environment": app_settings.app_env,
            "facility": facility_settings.facility_name,
            "firmware": hardware_settings.hardware_firmware_version,
        }

    return application


app = create_application()
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./laundry.db"
    secret_key: str = "replace-with-strong-random-key"
    session_cookie: str = "laundry_session"
    session_max_age_seconds: int = 60 * 60 * 24

    class Config:
        env_file = ".env"
        extra = "ignore"


class FacilitySettings(BaseSettings):
    facility_name: str = "Laundry Operations Hub"
    facility_short_code: str = "LOP"
    facility_location: str = "Unknown"
    facility_currency_symbol: str = "$"
    facility_currency_code: str = "USD"
    facility_hotline: str = ""
    facility_support_email: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


class HardwareSettings(BaseSettings):
    hardware_firmware_version: str = "v1.0.0"
    hardware_gateway_ip: str = "127.0.0.1"
    hardware_gateway_port: int = 1883
    hardware_max_load_kg: float = 12.0
    hardware_default_cycle_minutes: int = 35
    hardware_price_per_kg: float = 60.0
    hardware_minimum_kg: float = 1.0

    class Config:
        env_file = ".env"
        extra = "ignore"


app_settings = AppSettings()
facility_settings = FacilitySettings()
hardware_settings = HardwareSettings()
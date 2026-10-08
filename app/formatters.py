from config.facility import CYCLE_PROGRAMS
from config.settings import facility_settings, hardware_settings


def format_currency(amount: float, symbol: str | None = None) -> str:
    sym = symbol or facility_settings.facility_currency_symbol
    return f"{sym}{amount:,.2f}"


def format_station(station_number: int) -> str:
    return f"Station {station_number:02d}"


def format_bay_label(station_number: int) -> str:
    return f"Bay #{station_number:02d}"


def format_load(kilograms: float) -> str:
    return f"{kilograms:.2f} kg"


def format_capacity_percentage(load_kg: float, capacity_kg: float) -> float:
    if capacity_kg <= 0:
        return 0.0
    return min((load_kg / capacity_kg) * 100, 100.0)


def format_temperature(celsius: int | None) -> str:
    return f"{celsius}°C" if celsius is not None else "—"


def format_rotation(rpm: int | None) -> str:
    return f"{rpm} rpm" if rpm is not None else "—"


def format_duration(minutes: int) -> str:
    return f"{minutes}m" if minutes > 0 else "Ready"


def format_state_label(state_value: str) -> str:
    labels = {
        "available": "Ready / Idle",
        "running": "Washing",
        "extracting": "Spinning",
        "finished": "Complete",
        "out_of_service": "Maintenance",
    }
    return labels.get(state_value, state_value.replace("_", " ").title())


def resolve_cycle(cycle_key: str) -> dict:
    return CYCLE_PROGRAMS.get(cycle_key, CYCLE_PROGRAMS["standard"])


def compute_duration(cycle_key: str, measured_kg: float) -> int:
    program = resolve_cycle(cycle_key)
    base = program.get("base_minutes", 20)
    per_kg = program.get("minutes_per_kg", 4)
    total = base + measured_kg * per_kg
    return max(1, int(round(total)))


def compute_price(measured_kg: float) -> float:
    return round(measured_kg * hardware_settings.hardware_price_per_kg, 2)


def compute_imperial_pounds(kilograms: float) -> float:
    return round(kilograms * 2.20462, 2)
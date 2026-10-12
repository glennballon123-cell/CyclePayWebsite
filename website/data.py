from datetime import datetime
FACILITY_NAME = "Laundry Operations Hub"
FACILITY_LOCATION = "Unknown"
FACILITY_SHORT_CODE = "LOP"
FACILITY_CURRENCY_SYMBOL = "₱"
FACILITY_HOTLINE = ""
FACILITY_SUPPORT_EMAIL = ""

HARDWARE_FIRMWARE = "v1.0.0"
HARDWARE_MAX_LOAD_KG = 12.0
HARDWARE_PRICE_PER_KG = 60.0
HARDWARE_MINIMUM_KG = 1.0

CYCLE_PROGRAMS = {
    "light": {"label": "Quick Wash", "base_minutes": 10, "minutes_per_kg": 3, "price_per_kg": 45.0, "temperature_celsius": 30, "rotation_rpm": 600},
    "standard": {"label": "Deep Clean & Sanitize", "base_minutes": 20, "minutes_per_kg": 4, "price_per_kg": 60.0, "temperature_celsius": 60, "rotation_rpm": 780},
    "heavy": {"label": "Heavy Duty", "base_minutes": 25, "minutes_per_kg": 5, "price_per_kg": 75.0, "temperature_celsius": 70, "rotation_rpm": 850},
    "delicate": {"label": "Delicate & Wool", "base_minutes": 15, "minutes_per_kg": 3, "price_per_kg": 55.0, "temperature_celsius": 40, "rotation_rpm": 500},
    "drying": {"label": "Moisture-Sense Dry", "base_minutes": 20, "minutes_per_kg": 4, "price_per_kg": 50.0, "temperature_celsius": 55, "rotation_rpm": 900},
}

STATE_LABELS = {
    "available": "Ready / Idle",
    "running": "Washing",
    "extracting": "Spinning",
    "finished": "Complete",
    "out_of_service": "Maintenance",
}

EQUIPMENT_STATES = ["available", "running", "extracting", "finished", "out_of_service"]


def format_currency(amount):
    return f"{FACILITY_CURRENCY_SYMBOL}{amount:,.2f}"


def format_bay_label(station_number):
    return f"Bay #{station_number:02d}"


def format_load(kilograms):
    return f"{kilograms:.2f} kg"


def format_temperature(celsius):
    return f"{celsius}°C" if celsius is not None else "—"


def format_rotation(rpm):
    return f"{rpm} rpm" if rpm is not None else "—"


def format_duration(minutes):
    if not minutes or minutes <= 0:
        return "Ready"
    return f"{minutes}m"


def format_state_label(state_value):
    return STATE_LABELS.get(state_value, state_value.replace("_", " ").title())


def format_capacity_percentage(load_kg, capacity_kg):
    if capacity_kg <= 0:
        return 0.0
    return min((load_kg / capacity_kg) * 100, 100.0)


from datetime import datetime


def format_moment(moment):
    if isinstance(moment, str):
        moment = datetime.fromisoformat(moment)
    return moment.strftime("%b %d, %Y %I:%M %p")


def format_clock(moment):
    if isinstance(moment, str):
        moment = datetime.fromisoformat(moment)
    return moment.strftime("%H:%M:%S")


def resolve_cycle(cycle_key):
    return CYCLE_PROGRAMS.get(cycle_key, CYCLE_PROGRAMS["standard"])


def compute_duration(cycle_key, measured_kg):
    program = resolve_cycle(cycle_key)
    return max(1, int(round(program["base_minutes"] + measured_kg * program["minutes_per_kg"])))


def compute_price(measured_kg, cycle_key="standard"):
    program = resolve_cycle(cycle_key)
    return round(measured_kg * program["price_per_kg"], 2)


def build_instrument_code(station_number, sequence):
    return f"{FACILITY_SHORT_CODE}-{station_number:02d}{sequence:04d}"
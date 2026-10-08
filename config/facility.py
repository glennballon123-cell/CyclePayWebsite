from dataclasses import dataclass


@dataclass(frozen=True)
class ReferencePrefix:
    settlement: str
    access: str
    measurement: str
    administration: str
    notification: str


REFERENCE_PREFIXES = ReferencePrefix(
    settlement="STL",
    access="ACS",
    measurement="MSR",
    administration="ADM",
    notification="NTF",
)


CYCLE_PROGRAMS = {
    "light": {
        "label": "Quick Wash",
        "base_minutes": 10,
        "minutes_per_kg": 3,
        "temperature_celsius": 30,
        "rotation_rpm": 600,
    },
    "standard": {
        "label": "Deep Clean & Sanitize",
        "base_minutes": 20,
        "minutes_per_kg": 4,
        "temperature_celsius": 60,
        "rotation_rpm": 780,
    },
    "heavy": {
        "label": "Heavy Duty",
        "base_minutes": 25,
        "minutes_per_kg": 5,
        "temperature_celsius": 70,
        "rotation_rpm": 850,
    },
    "delicate": {
        "label": "Delicate & Wool",
        "base_minutes": 15,
        "minutes_per_kg": 3,
        "temperature_celsius": 40,
        "rotation_rpm": 500,
    },
    "drying": {
        "label": "Moisture-Sense Dry",
        "base_minutes": 20,
        "minutes_per_kg": 4,
        "temperature_celsius": 55,
        "rotation_rpm": 900,
    },
}
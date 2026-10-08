import hashlib
from datetime import datetime

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from config.facility import REFERENCE_PREFIXES
from config.settings import app_settings, facility_settings


def build_instrument_code(station_number: int, sequence: int) -> str:
    prefix = facility_settings.facility_short_code
    return f"{prefix}-{station_number:02d}{sequence:04d}"


def build_reference(kind: str, code: str) -> str:
    prefix = getattr(REFERENCE_PREFIXES, kind, "REF")
    return f"{prefix}-{code}"


def build_integrity_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_occurred_at_label(moment: datetime | None = None) -> str:
    moment = moment or datetime.utcnow()
    return moment.isoformat(timespec="seconds")


def _token_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(app_settings.secret_key)


def sign_voucher_payload(code: str) -> str:
    return _token_serializer().dumps({"code": code})


def verify_voucher_payload(token: str, max_age_seconds: int = 86400) -> dict | None:
    try:
        return _token_serializer().loads(token, max_age=max_age_seconds)
    except (BadSignature, SignatureExpired):
        return None

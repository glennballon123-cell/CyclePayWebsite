import bcrypt
from itsdangerous import URLSafeTimedSerializer

from config.settings import app_settings


_token_serializer = URLSafeTimedSerializer(app_settings.secret_key)


def hash_credential(plain: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_credential(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def issue_session_token(account_id: int) -> str:
    return _token_serializer.dumps({"account_id": account_id})


def parse_session_token(token: str) -> dict:
    try:
        return _token_serializer.loads(token, max_age=app_settings.session_max_age_seconds)
    except Exception:
        return {}
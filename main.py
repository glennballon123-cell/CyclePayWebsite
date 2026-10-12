import traceback

try:
    from website.app import app
except Exception:
    traceback.print_exc()
    raise
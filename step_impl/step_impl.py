from getgauge.python import step, before_suite
import os
import requests

API_BASE = os.getenv("API_URL", "http://localhost:8000/api/v1")
HEALTH_URL = API_BASE.rsplit("/api/v1", 1)[0] + "/health"
_storage = {}


@before_suite()
def before_suite_hook():
    try:
        requests.get(HEALTH_URL, timeout=2)
    except Exception:
        pass


@step("Check health, should be ok")
def check_health():
    r = requests.get(HEALTH_URL, timeout=5)
    assert r.status_code == 200, f"health failed: {r.status_code} {r.text}"

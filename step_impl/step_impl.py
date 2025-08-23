from getgauge.python import before_suite, after_suite, Messages
import os
import requests

API_BASE = os.getenv("API_URL", "http://localhost:8000/")
HEALTH_URL = API_BASE + "/health"
_storage = {}


@before_suite()
def before_suite_hook():
    try:
        requests.get(HEALTH_URL, timeout=2)
    except Exception:
        pass


@after_suite()
def after_suite_hook():
    """
    Cleanup: delete all tasks at the end of the test run.
    This calls GET /api/v1/tasks and then DELETE /api/v1/tasks/{id} for each item.
    """
    base = API_BASE.rstrip("/")
    TASKS_URL = f"{base}/api/v1/tasks"
    try:
        r = requests.get(TASKS_URL, timeout=5)
    except Exception as e:
        Messages.write_message(f"Cleanup: failed to list tasks: {e}")
        return

    if r.status_code != 200:
        Messages.write_message(
            f"Cleanup: list tasks returned {r.status_code}; skipping cleanup"
        )
        return

    try:
        arr = r.json()
    except Exception as e:
        Messages.write_message(f"Cleanup: failed to parse list response: {e}")
        return

    deleted = 0
    for t in arr:
        tid = t.get("id")
        if not tid:
            continue
        try:
            dr = requests.delete(f"{TASKS_URL}/{tid}", timeout=5)
            if dr.status_code in (200, 204):
                deleted += 1
                Messages.write_message(f"Cleanup: deleted task {tid}")
            elif dr.status_code in (400, 404):
                Messages.write_message(
                    f"Cleanup: task {tid} already gone ({dr.status_code})"
                )
            else:
                Messages.write_message(
                    f"Cleanup: failed to delete {tid}, status={dr.status_code} body={dr.text}"
                )
        except Exception as e:
            Messages.write_message(f"Cleanup: exception deleting {tid}: {e}")

    Messages.write_message(f"Cleanup finished. Deleted {deleted} tasks.")

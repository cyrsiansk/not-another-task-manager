from getgauge.python import step, Messages, data_store
import os
import requests
from uuid import uuid4

API_BASE = os.getenv("API_URL", "http://localhost:8000/api/v1")
REGISTER_URL = f"{API_BASE}/auth/register"
TOKEN_URL = f"{API_BASE}/auth/token"
TASKS_URL = f"{API_BASE}/tasks"
HEALTH_URL = API_BASE.rsplit("/api/v1", 1)[0] + "/health"


def _post_register(email: str, password: str):
    return requests.post(
        REGISTER_URL, json={"email": email, "password": password}, timeout=5
    )


def _post_token(email: str, password: str):
    return requests.post(
        TOKEN_URL, data={"username": email, "password": password}, timeout=5
    )


def _auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


@step("Create task with title <title> and description <description>")
def step_create_task(title, description):
    token = data_store.scenario.get("auth_token")
    assert token, "auth token missing"
    payload = {"title": title, "description": description}
    r = requests.post(TASKS_URL, json=payload, headers=_auth_headers(token), timeout=5)
    assert r.status_code == 201, f"Create task failed: {r.status_code} {r.text}"
    j = r.json()
    data_store.scenario["task_id"] = j.get("id")
    Messages.write_message(f"Created task {j.get('id')} title={title}")


@step("Fetch task by id and check title is <title>")
def step_fetch_task_and_check_title(title):
    token = data_store.scenario.get("auth_token")
    task_id = data_store.scenario.get("task_id")
    assert token and task_id, "missing token or task_id"
    r = requests.get(f"{TASKS_URL}/{task_id}", headers=_auth_headers(token), timeout=5)
    assert r.status_code == 200, f"Get task failed: {r.status_code} {r.text}"
    j = r.json()
    assert j.get("title") == title, f"Title mismatch: {j.get('title')} != {title}"
    Messages.write_message(f"Fetched task {task_id}, title OK")


@step("Update task title to <title> and check updated")
def step_update_task_title_and_check(title):
    token = data_store.scenario.get("auth_token")
    task_id = data_store.scenario.get("task_id")
    assert token and task_id
    r = requests.get(f"{TASKS_URL}/{task_id}", headers=_auth_headers(token), timeout=5)
    assert r.status_code == 200
    obj = r.json()
    version = obj.get("version")
    payload = {"title": title, "version": version}
    r2 = requests.patch(
        f"{TASKS_URL}/{task_id}", json=payload, headers=_auth_headers(token), timeout=5
    )
    assert r2.status_code == 200, f"Update failed: {r2.status_code} {r2.text}"
    j = r2.json()
    assert j.get("title") == title
    data_store.scenario["task_version"] = j.get("version")
    Messages.write_message(f"Updated task {task_id} to title={title}")


@step("Set task status to <status>")
def step_set_task_status(status):
    token = data_store.scenario.get("auth_token")
    task_id = data_store.scenario.get("task_id")
    assert token and task_id
    r = requests.get(f"{TASKS_URL}/{task_id}", headers=_auth_headers(token), timeout=5)
    assert r.status_code == 200
    version = r.json().get("version")
    payload = {"status": status, "version": version}
    r2 = requests.patch(
        f"{TASKS_URL}/{task_id}", json=payload, headers=_auth_headers(token), timeout=5
    )
    assert r2.status_code == 200, f"Set status failed: {r2.status_code} {r2.text}"
    Messages.write_message(f"Set task {task_id} status -> {status}")


@step("Delete task (expect success)")
def step_delete_task():
    token = data_store.scenario.get("auth_token")
    task_id = data_store.scenario.get("task_id")
    r = requests.delete(
        f"{TASKS_URL}/{task_id}", headers=_auth_headers(token), timeout=5
    )
    assert r.status_code in (200, 204), f"Delete failed: {r.status_code} {r.text}"
    Messages.write_message(f"Deleted task {task_id}")


@step("Fetch deleted task by id (expect not found)")
def step_fetch_deleted_task_expect_not_found():
    token = data_store.scenario.get("auth_token")
    task_id = data_store.scenario.get("task_id")
    r = requests.get(f"{TASKS_URL}/{task_id}", headers=_auth_headers(token), timeout=5)
    assert r.status_code in (
        400,
        404,
    ), f"Expected not found but got: {r.status_code} {r.text}"
    Messages.write_message(f"Fetching deleted task returned {r.status_code}")


@step("Create task with title <title> and status <status>")
def step_create_task_with_status(title, status):
    token = data_store.scenario.get("auth_token")
    payload = {"title": title}
    if "description" in data_store.scenario:
        payload["description"] = data_store.scenario.get("description")
    r = requests.post(TASKS_URL, json=payload, headers=_auth_headers(token), timeout=5)
    assert r.status_code == 201, f"Create task failed: {r.status_code} {r.text}"
    j = r.json()
    tid = j.get("id")
    if status and status != "created":
        v = j.get("version")
        pr = requests.patch(
            f"{TASKS_URL}/{tid}",
            json={"status": status, "version": v},
            headers=_auth_headers(token),
            timeout=5,
        )
        assert pr.status_code == 200
    Messages.write_message(f"Created task {tid} status={status}")


@step(
    "List tasks with status <status> and check only tasks with that status are returned"
)
def step_list_tasks_with_status_check(status):
    token = data_store.scenario.get("auth_token")
    params = {"status": status}
    r = requests.get(TASKS_URL, headers=_auth_headers(token), params=params, timeout=5)
    assert r.status_code == 200, f"List failed: {r.status_code} {r.text}"
    arr = r.json()
    assert all(
        (t.get("status") == status for t in arr)
    ), f"Found items with other statuses: {[t.get('status') for t in arr]}"
    Messages.write_message(f"List with status={status} returned {len(arr)} items")


@step("List tasks with limit <limit> and check no more than that limit is returned")
def step_list_tasks_with_limit_check(limit: int):
    token = data_store.scenario.get("auth_token")
    params = {"limit": int(limit)}
    r = requests.get(TASKS_URL, headers=_auth_headers(token), params=params, timeout=5)
    assert r.status_code == 200, f"List failed: {r.status_code} {r.text}"
    arr = r.json()
    assert len(arr) <= int(limit), f"Returned {len(arr)} items, expected <= {limit}"
    Messages.write_message(f"List with limit={limit} returned {len(arr)} items")


@step("Update task with current version (expect success)")
def step_update_with_current_version():
    token = data_store.scenario.get("auth_token")
    task_id = data_store.scenario.get("task_id")
    r = requests.get(f"{TASKS_URL}/{task_id}", headers=_auth_headers(token), timeout=5)
    assert r.status_code == 200
    v = r.json().get("version")
    payload = {"title": "lock-updated", "version": v}
    r2 = requests.patch(
        f"{TASKS_URL}/{task_id}", json=payload, headers=_auth_headers(token), timeout=5
    )
    assert r2.status_code == 200
    data_store.scenario["task_version"] = r2.json().get("version")
    Messages.write_message("Updated with current version OK")


@step("Attempt update with stale version (expect 409)")
def step_attempt_update_stale_version_expect_409():
    token = data_store.scenario.get("auth_token")
    task_id = data_store.scenario.get("task_id")
    stale_version = max(1, data_store.scenario.get("task_version", 1) - 1)
    payload = {"title": "stale-update", "version": stale_version}
    r = requests.patch(
        f"{TASKS_URL}/{task_id}", json=payload, headers=_auth_headers(token), timeout=5
    )
    assert r.status_code == 409, f"Expected 409 but got {r.status_code} {r.text}"
    Messages.write_message("Stale update returned 409 as expected")


@step("Create and login as another user")
def step_create_and_login_another_user():
    username = f"user_{uuid4().hex[:8]}"
    email = f"{username}@gmail.com"
    password = "Aa1!pass12345"
    r = _post_register(email, password)
    assert r.status_code in (200, 201)
    rt = _post_token(email, password)
    assert rt.status_code == 200
    token = rt.json().get("access_token") or rt.json().get("token")
    data_store.scenario["alt_email"] = email
    data_store.scenario["alt_password"] = password
    data_store.scenario["alt_token"] = token
    Messages.write_message(f"Created alt user {email}")


@step("Attempt to fetch the first user's task by id (expect not found)")
def step_alt_user_cannot_fetch_task():
    task_id = data_store.scenario.get("task_id")
    token = data_store.scenario.get("alt_token")
    assert task_id and token
    r = requests.get(f"{TASKS_URL}/{task_id}", headers=_auth_headers(token), timeout=5)
    assert r.status_code in (
        400,
        404,
    ), f"Expected not found but got {r.status_code} {r.text}"
    Messages.write_message(f"Alt user fetch returned {r.status_code}")


@step("Send request to GET /tasks without token (expect 401)")
def step_get_tasks_without_token_expect_401():
    r = requests.get(TASKS_URL, timeout=5)
    assert r.status_code in (
        401,
        403,
    ), f"Expected unauthorized but got {r.status_code} {r.text}"
    Messages.write_message(f"GET /tasks without token returned {r.status_code}")


@step("Delete task again (expect not found)")
def step_delete_task_again_expect_not_found():
    token = data_store.scenario.get("auth_token")
    task_id = data_store.scenario.get("task_id")
    assert task_id, "missing task_id for second-delete check"

    r = requests.delete(
        f"{TASKS_URL}/{task_id}", headers=_auth_headers(token), timeout=5
    )

    assert r.status_code in (
        400,
        404,
    ), f"Expected not found on second delete but got {r.status_code}: {r.text}"
    Messages.write_message(f"Second delete returned {r.status_code}")

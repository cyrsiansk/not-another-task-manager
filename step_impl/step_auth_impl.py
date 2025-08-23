from getgauge.python import (
    step,
    before_suite,
    before_scenario,
    data_store,
    Messages,
)
import os
import requests
import secrets
import string
from uuid import uuid4

API_BASE = os.getenv("API_URL", "http://localhost:8000/api/v1")
REGISTER_URL = f"{API_BASE}/auth/register"
TOKEN_URL = f"{API_BASE}/auth/token"
TASKS_URL = f"{API_BASE}/tasks"
HEALTH_URL = API_BASE.rsplit("/api/v1", 1)[0] + "/health"

SPECIALS = "!@#$%^&*()-_+={}[]"
PASSWORD_LENGTH = 12


@before_suite()
def before_suite_hook():
    try:
        requests.get(HEALTH_URL, timeout=2)
    except Exception:
        pass


def _generate_password(length: int = PASSWORD_LENGTH) -> str:
    if length < 8:
        raise ValueError("password length must be >= 8")
    upper = secrets.choice(string.ascii_uppercase)
    lower = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    special = secrets.choice(SPECIALS)
    remaining = [
        secrets.choice(string.ascii_letters + string.digits + SPECIALS)
        for _ in range(length - 4)
    ]
    pwd_chars = [upper, lower, digit, special] + remaining
    secrets.SystemRandom().shuffle(pwd_chars)
    return "".join(pwd_chars)


@before_scenario
def before_scenario_generate_user(context=None):
    username = f"user_{uuid4().hex[:8]}"
    email = f"{username}@gmail.com"
    password = _generate_password(PASSWORD_LENGTH)
    alt_password = _generate_password(PASSWORD_LENGTH)

    data_store.scenario["username"] = username
    data_store.scenario["email"] = email
    data_store.scenario["password"] = password
    data_store.scenario["alt_password"] = alt_password

    masked = password[:-4] + "****"
    Messages.write_message(
        f"[setup] Generated user: {username}, email: {email}, password: {masked}"
    )


def _post_register(email: str, password: str) -> requests.Response:
    payload = {"email": email, "password": password}
    return requests.post(REGISTER_URL, json=payload, timeout=5)


def _post_token(email: str, password: str) -> requests.Response:
    return requests.post(
        TOKEN_URL, data={"username": email, "password": password}, timeout=5
    )


@step("Generate random credentials")
def step_generate_random_credentials():
    if "email" not in data_store.scenario:
        before_scenario_generate_user()
    Messages.write_message(f"Using generated email: {data_store.scenario['email']}")


@step("Register user via API (expect success)")
def step_register_user_expect_success():
    email = data_store.scenario["email"]
    password = data_store.scenario["password"]

    r = _post_register(email, password)
    assert r.status_code in (
        200,
        201,
    ), f"Expected success but got {r.status_code}: {r.text}"

    try:
        j = r.json()
        if isinstance(j, dict) and "id" in j:
            data_store.scenario["user_id"] = j["id"]
    except ValueError:
        pass

    Messages.write_message(f"Registered {email} (status {r.status_code})")


@step("Attempt to register user via API with invalid password (expect failure)")
def step_register_invalid_password_expect_failure():
    email = data_store.scenario["email"]
    bad_password = "short"
    r = _post_register(email, bad_password)
    assert (
        r.status_code >= 400
    ), f"Expected registration to fail but got {r.status_code}"
    Messages.write_message(
        f"Attempted invalid registration for {email}, got {r.status_code}: {r.text[:200]}"
    )


@step("Attempt to login with those invalid credentials (expect failure)")
def step_login_invalid_credentials_expect_failure():
    email = data_store.scenario["email"]
    bad_password = "short"
    r = _post_token(email, bad_password)
    assert r.status_code >= 400, f"Expected login to fail but got {r.status_code}"
    Messages.write_message(f"Login attempt with invalid creds returned {r.status_code}")


@step("Register same user again via API (expect failure)")
def step_register_same_user_again_expect_failure():
    email = data_store.scenario["email"]
    password = data_store.scenario["password"]
    r = _post_register(email, password)
    assert (
        r.status_code >= 400
    ), f"Expected duplicate registration to fail but got {r.status_code}"
    Messages.write_message(f"Duplicate registration returned {r.status_code}")


@step("Attempt to register same email with a different password (expect failure)")
def step_register_same_email_with_different_password_expect_failure():
    email = data_store.scenario["email"]
    alt_password = data_store.scenario["alt_password"]
    r = _post_register(email, alt_password)
    assert (
        r.status_code >= 400
    ), f"Expected re-registration with different password to fail but got {r.status_code}"
    Messages.write_message(
        f"Re-registration with different password returned {r.status_code}"
    )


@step("Attempt to login with the different password (expect failure)")
def step_login_with_different_password_expect_failure():
    email = data_store.scenario["email"]
    alt_password = data_store.scenario["alt_password"]
    r = _post_token(email, alt_password)
    assert (
        r.status_code >= 400
    ), f"Expected login with alt password to fail but got {r.status_code}"
    Messages.write_message(f"Login with alt password returned {r.status_code}")


@step("Login with credentials (expect success)")
def step_login_expect_success():
    email = data_store.scenario["email"]
    password = data_store.scenario["password"]
    r = _post_token(email, password)
    assert r.status_code == 200, f"Login failed ({r.status_code}): {r.text}"
    data = r.json()
    token = data.get("access_token") or data.get("token")
    assert token, f"No token in login response: {data}"
    data_store.scenario["auth_token"] = token
    Messages.write_message("Login OK, token stored in scenario store.")


@step("Login with original password (expect success)")
def step_login_original_expect_success():
    step_login_expect_success()


@step("Fetch tasks for the user (expect success)")
def step_fetch_tasks_expect_success():
    token = data_store.scenario.get("auth_token")
    assert token, "auth token missing; login probably failed"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(TASKS_URL, headers=headers, timeout=5)
    assert r.status_code == 200, f"Fetching tasks failed ({r.status_code}): {r.text}"
    tasks = r.json()
    assert isinstance(tasks, list), "Tasks response is not a list"
    Messages.write_message(f"Fetched {len(tasks)} task(s) for user.")

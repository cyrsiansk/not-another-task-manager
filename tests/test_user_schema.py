import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate, UserRead
from uuid import uuid4
from datetime import datetime

correct_emails = [
    "user@example.com",
    "user.name+tag+sorting@example.com",
    "user_name@example.co.uk",
    "user-name@sub.domain.example",
    "я@мой.рф",
]

incorrect_emails = [
    "plainaddress",
    "@missing-user.com",
    "user@.com",
    "user@com",
    "user@@example.com",
    "user example@example.com",
    "",
]

incorrect_uuids = ["test", str(uuid4()) + "1", "", str(uuid4())[:-1] + "s"]


@pytest.mark.parametrize("email", correct_emails)
def test_usercreate_valid_emails(email):
    obj = UserCreate(email=email, password="strongpasSword!@#2")
    assert obj.email == email
    assert obj.password.get_secret_value() == "strongpasSword!@#2"


@pytest.mark.parametrize("email", incorrect_emails)
def test_usercreate_invalid_emails(email):
    with pytest.raises(ValidationError):
        UserCreate(email=email, password="pwd")


@pytest.mark.parametrize("email", correct_emails)
def test_valid_userread_schema(email):
    uuid = uuid4()
    created_at = datetime.now()
    obj = UserRead(id=uuid, email=email, created_at=created_at)
    assert obj.id == uuid
    assert obj.email == email
    assert obj.created_at == created_at


@pytest.mark.parametrize("email", incorrect_emails)
def test_invalid_userread_schema(email):
    with pytest.raises(ValidationError):
        UserRead(id=uuid4(), email=email, created_at=datetime.now())


@pytest.mark.parametrize("uuid", incorrect_uuids)
def test_invalid_userread_uuid(uuid):
    with pytest.raises(ValidationError):
        UserRead(id=uuid, email="user@example.com", created_at=datetime.now())

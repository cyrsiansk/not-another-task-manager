import pytest
from datetime import timedelta
from jose import JWTError

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_hash_and_verify_password():
    plain = "super-secret"
    hashed = hash_password(plain)
    assert isinstance(hashed, str)
    assert verify_password(plain, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_verify_password_none_or_empty_hashed_returns_false():
    assert verify_password("whatever", None) is False
    assert verify_password("whatever", "") is False


def test_create_and_decode_token():
    token = create_access_token(subject="12345", expires_delta=timedelta(minutes=5))
    assert isinstance(token, str)
    payload = decode_access_token(token)
    assert payload.get("sub") == "12345"
    assert "exp" in payload


def test_decode_invalid_token_raises():
    with pytest.raises(JWTError):
        decode_access_token("this.is.not.a.valid.token")


def test_decode_expired_token_raises():
    expired_token = create_access_token(
        subject="expired", expires_delta=timedelta(seconds=-1)
    )
    with pytest.raises(JWTError):
        decode_access_token(expired_token)

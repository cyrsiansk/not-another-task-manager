# tests/test_password_validation.py
from pydantic import SecretStr
import pytest

# Поправь импорт, если разместишь валидатор в другом модуле
from app.schemas.user import validate_password


def test_valid_password_passes():
    pw = SecretStr("Aa1!aaaa")
    res = validate_password(pw)
    assert isinstance(res, SecretStr)
    assert res.get_secret_value() == "Aa1!aaaa"


@pytest.mark.parametrize(
    "pw",
    [
        ("A1!a"),
        ("short1!"),
    ],
)
def test_too_short_password_raises(pw):
    with pytest.raises(ValueError):
        validate_password(SecretStr(pw))


def test_too_long_password_raises():
    long_pw = "A" * 31 + "a1!"
    with pytest.raises(ValueError):
        validate_password(SecretStr(long_pw))


def test_missing_number_raises():
    with pytest.raises(ValueError) as exc:
        validate_password(SecretStr("Abcdefg!"))
    assert "numeral" in str(exc.value).lower()


def test_missing_uppercase_raises():
    with pytest.raises(ValueError) as exc:
        validate_password(SecretStr("abcdef1!"))
    assert "uppercase" in str(exc.value).lower()


def test_missing_lowercase_raises():
    with pytest.raises(ValueError) as exc:
        validate_password(SecretStr("ABCDEF1!"))
    assert "lowercase" in str(exc.value).lower()


def test_missing_special_char_raises():
    with pytest.raises(ValueError) as exc:
        validate_password(SecretStr("Abcdef11"))
    assert ("symbol" in str(exc.value).lower()) or ("{" in str(exc.value))


def test_non_string_get_secret_value_raises_typeerror():
    class Dummy:
        def get_secret_value(self):
            return 123

    with pytest.raises(TypeError):
        validate_password(Dummy())

from pydantic import BaseModel, EmailStr, SecretStr, AfterValidator
from uuid import UUID
from datetime import datetime
from typing import Optional, Annotated

SPECIAL_CHARS: set[str] = {
    "$",
    "@",
    "#",
    "%",
    "!",
    "^",
    "&",
    "*",
    "(",
    ")",
    "-",
    "_",
    "+",
    "=",
    "{",
    "}",
    "[",
    "]",
}


MIN_LENGTH: int = 8
MAX_LENGTH: int = 30
INCLUDES_SPECIAL_CHARS: bool = True
INCLUDES_NUMBERS: bool = True
INCLUDES_LOWERCASE: bool = True
INCLUDES_UPPERCASE: bool = True


def validate_password(v: SecretStr) -> SecretStr:
    min_length = MIN_LENGTH
    max_length = MAX_LENGTH
    includes_special_chars = INCLUDES_SPECIAL_CHARS
    includes_numbers = INCLUDES_NUMBERS
    includes_lowercase = INCLUDES_LOWERCASE
    includes_uppercase = INCLUDES_UPPERCASE
    special_chars = SPECIAL_CHARS

    if not isinstance(v.get_secret_value(), str):
        raise TypeError("string required")
    if len(v.get_secret_value()) < min_length or len(v.get_secret_value()) > max_length:
        raise ValueError(
            f"length should be at least {min_length} but not more than {max_length}"
        )

    if includes_numbers and not any(char.isdigit() for char in v.get_secret_value()):
        raise ValueError("Password should have at least one numeral")

    if includes_uppercase and not any(char.isupper() for char in v.get_secret_value()):
        raise ValueError("Password should have at least one uppercase letter")

    if includes_lowercase and not any(char.islower() for char in v.get_secret_value()):
        raise ValueError("Password should have at least one lowercase letter")

    if includes_special_chars and not any(
        char in special_chars for char in v.get_secret_value()
    ):
        raise ValueError(
            f"Password should have at least one of the symbols {special_chars}"
        )

    return v


ValidatePassword = Annotated[SecretStr, AfterValidator(validate_password)]


class UserCreate(BaseModel):
    email: EmailStr
    password: ValidatePassword


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None

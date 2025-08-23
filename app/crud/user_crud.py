from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.models.user import User
from app.schemas.user import ValidatePassword
from app.core.security import hash_password, verify_password


def create_user(db: Session, email: str, password: ValidatePassword) -> User:
    hashed = hash_password(password.get_secret_value())
    user = User(email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalars().first()


def get_user(db: Session, user_id: UUID) -> Optional[User]:
    stmt = select(User).where(User.id == user_id)
    return db.execute(stmt).scalars().first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user: User = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

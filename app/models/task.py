import enum
import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    Enum as SAEnum,
    TIMESTAMP,
    func,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base import Base


class TaskStatus(str, enum.Enum):
    created = "created"
    in_progress = "in_progress"
    done = "done"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(
        SAEnum(TaskStatus, name="task_status"),
        nullable=False,
        default=TaskStatus.created,
    )
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)
    version = Column(Integer, nullable=False, default=1)

from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    version: Optional[int] = None


class TaskRead(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    version: int

    model_config = {"from_attributes": True}

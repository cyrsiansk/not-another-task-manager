# tests/test_models_and_schemas.py
from uuid import UUID
from datetime import datetime

import pytest

from app.models.task import TaskStatus
from app.models.task import Task
from app.models.user import User
from app.models import __all__ as models_all


def test_taskstatus_values_and_types():
    assert TaskStatus.created.value == "created"
    assert TaskStatus.in_progress.value == "in_progress"
    assert TaskStatus.done.value == "done"
    assert TaskStatus("done") is TaskStatus.done
    assert isinstance(str(TaskStatus.created), str)


def test_models_registered_and_tablenames():
    assert "User" in models_all
    assert "Task" in models_all

    assert getattr(User, "__tablename__", None) == "users"
    assert getattr(Task, "__tablename__", None) == "tasks"


def test_user_model_instantiation_minimal():
    u = User(email="test@example.com")
    assert hasattr(u, "email")
    assert u.email == "test@example.com"
    assert hasattr(u, "created_at")


@pytest.mark.parametrize(
    "dummy_attrs",
    [
        {
            "id": str(UUID(int=1)),
            "user_id": str(UUID(int=2)),
            "title": "Example",
            "description": None,
            "status": "created",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "version": 1,
        }
    ],
)
def test_task_read_schema_from_dict_like(dummy_attrs):
    from app.schemas.task import TaskRead
    from app.models.task import TaskStatus

    obj = TaskRead(**dummy_attrs)
    assert obj.title == "Example"
    assert obj.status in TaskStatus

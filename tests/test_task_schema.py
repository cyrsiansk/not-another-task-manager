import pytest
from pydantic import ValidationError

from app.schemas.task import TaskCreate, TaskUpdate, TaskRead
from app.models.task import TaskStatus
from uuid import uuid4
from datetime import datetime


def test_taskcreate_valid():
    obj = TaskCreate(title="Short title", description="desc")
    assert obj.title == "Short title"
    assert obj.description == "desc"


def test_taskcreate_title_too_long():
    too_long = "x" * 256
    with pytest.raises(ValidationError):
        TaskCreate(title=too_long)


@pytest.mark.parametrize("status_input", [TaskStatus.done, "done"])
def test_taskupdate_accepts_enum_and_string(status_input):
    u = TaskUpdate(status=status_input, version=1)
    assert u.status == TaskStatus.done


def test_taskupdate_invalid_status():
    with pytest.raises(ValidationError):
        TaskUpdate(status="not_a_real_status")


def test_taskread_from_dict_like():
    data = {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "title": "t",
        "description": None,
        "status": "created",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "version": 1,
    }
    obj = TaskRead(**data)
    assert obj.title == "t"
    assert obj.status == TaskStatus.created

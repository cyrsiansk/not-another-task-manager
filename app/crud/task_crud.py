from sqlalchemy import select, update
from app.models.task import Task
from app.models.task import TaskStatus
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
from sqlalchemy import func


def create_task(db: Session, title: str, description: Optional[str] = None) -> Task:
    task = Task(title=title, description=description)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: UUID) -> Optional[Task]:
    stmt = select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
    res = db.execute(stmt).scalars().first()
    return res


def list_tasks(
    db: Session, status: Optional[TaskStatus] = None, limit: int = 50
) -> List[Task]:
    stmt = select(Task).where(Task.deleted_at.is_(None))
    if status:
        stmt = stmt.where(Task.status == status)
    stmt = stmt.order_by(Task.created_at.desc()).limit(limit)
    return db.execute(stmt).scalars().all()


def update_task(
    db: Session,
    task_id: UUID,
    data: dict,
    expected_version: Optional[int] = None,
) -> Optional[Task]:
    query = update(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
    if expected_version is not None:
        query = query.where(Task.version == expected_version)

    fields = {}
    if "title" in data and data["title"] is not None:
        fields["title"] = data["title"]
    if "description" in data and data["description"] is not None:
        fields["description"] = data["description"]
    if "status" in data and data["status"] is not None:
        # allow passing either TaskStatus or its value
        val = data["status"]
        # if an enum instance, convert to its value
        fields["status"] = val.value if hasattr(val, "value") else val

    # nothing to update
    if not fields:
        return get_task(db, task_id)

    # set updated_at and bump version (version uses SQL expression)
    fields["updated_at"] = func.now()
    fields["version"] = Task.version + 1

    res = db.execute(query.values(**fields))
    db.commit()

    # check if updated
    if res.rowcount == 0:
        return None
    return get_task(db, task_id)


def soft_delete_task(db: Session, task_id: UUID) -> bool:
    stmt = (
        update(Task)
        .where(Task.id == task_id, Task.deleted_at.is_(None))
        .values(deleted_at=func.now())
    )
    res = db.execute(stmt)
    db.commit()
    return res.rowcount > 0

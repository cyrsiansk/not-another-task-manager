from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.db.session import get_db
from app.crud.task_crud import (
    create_task,
    get_task,
    list_tasks,
    update_task,
    soft_delete_task,
)
from app.models.task import TaskStatus

router = APIRouter()


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def api_create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = create_task(db, title=payload.title, description=payload.description)
    return task


@router.get("/tasks", response_model=List[TaskRead])
def api_list_tasks(
    status: Optional[TaskStatus] = Query(
        None,
        description="Filter tasks by status. One of: 'created', 'in_progress', 'done'.",
    ),
    limit: int = Query(
        50, ge=1, le=100, description="Maximum number of items to return"
    ),
    db: Session = Depends(get_db),
):
    tasks = list_tasks(db, status=status, limit=limit)
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskRead)
def api_get_task(task_id: UUID, db: Session = Depends(get_db)):
    task = get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def api_update_task(task_id: UUID, payload: TaskUpdate, db: Session = Depends(get_db)):
    expected_version = payload.version
    obj = update_task(
        db,
        task_id=task_id,
        data=payload.model_dump(),
        expected_version=expected_version,
    )
    if obj is None:
        raise HTTPException(status_code=409, detail="Update conflict or task not found")
    return obj


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_task(task_id: UUID, db: Session = Depends(get_db)):
    ok = soft_delete_task(db, task_id=task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return None

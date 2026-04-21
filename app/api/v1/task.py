import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.task import Task
from repositories.task import TaskRepository
from services.task import TaskService
from schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_service(session: AsyncSession) -> TaskService:
    return TaskService(TaskRepository(session))


@router.post("", response_model=TaskRead, status_code=201)
async def create_task(
    payload: TaskCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    task = Task(**payload.model_dump())
    task.assigned_by = user.id
    return await service.create(task)


@router.get("", response_model=List[TaskRead])
async def list_my_tasks(
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if status:
        return await service.list_by_status(user.id, status)
    return await service.list_by_assignee(user.id, skip, limit)


@router.get("/overdue", response_model=List[TaskRead])
async def list_overdue_tasks(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).list_overdue(user.id)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    task = await service.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: uuid.UUID,
    payload: TaskUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    data = payload.model_dump(exclude_unset=True)
    result = await service.update(task_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@router.patch("/{task_id}/complete", response_model=TaskRead)
async def complete_task(
    task_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    result = await service.complete(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    task = await service.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await service.delete(task_id)

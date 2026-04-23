import uuid
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from repositories.notification import NotificationRepository
from services.notification import NotificationService
from schemas.notification import NotificationRead, UnreadCount

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _get_service(session: AsyncSession) -> NotificationService:
    return NotificationService(NotificationRepository(session))


@router.get("", response_model=List[NotificationRead])
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).list_by_user(user.id, skip, limit)


@router.get("/unread-count", response_model=UnreadCount)
async def get_unread_count(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    count = await _get_service(session).unread_count(user.id)
    return UnreadCount(count=count)


@router.patch("/{notification_id}/read", status_code=204)
async def mark_notification_read(
    notification_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    await _get_service(session).mark_read(notification_id)


@router.patch("/read-all", status_code=200)
async def mark_all_read(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    count = await _get_service(session).mark_all_read(user.id)
    return {"marked_read": count}

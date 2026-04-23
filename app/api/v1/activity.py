import uuid
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.activity import Activity
from repositories.activity import ActivityRepository
from services.activity import ActivityService
from schemas.activity import ActivityCreate, ActivityRead

router = APIRouter(tags=["activities"])


def _get_service(session: AsyncSession) -> ActivityService:
    return ActivityService(ActivityRepository(session))


@router.post("/leads/{lead_id}/activities", response_model=ActivityRead, status_code=201)
async def add_activity_to_lead(
    lead_id: uuid.UUID,
    payload: ActivityCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    activity = Activity(
        lead_id=lead_id,
        contact_id=payload.contact_id,
        property_id=payload.property_id,
        agent_id=payload.agent_id,
        activity_type=payload.activity_type,
        title=payload.title,
        description=payload.description,
        metadata_=payload.metadata_,
        scheduled_at=payload.scheduled_at,
    )
    activity.created_by = user.email
    return await service.create(activity)


@router.get("/leads/{lead_id}/activities", response_model=List[ActivityRead])
async def list_lead_activities(
    lead_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).list_by_lead(lead_id, skip, limit)


@router.get("/contacts/{contact_id}/activities", response_model=List[ActivityRead])
async def list_contact_activities(
    contact_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).list_by_contact(contact_id, skip, limit)


@router.get("/activities", response_model=List[ActivityRead])
async def list_activities(
    agent_id: uuid.UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if agent_id:
        return await service.list_by_agent(agent_id, skip, limit)
    return await service.list(skip, limit)

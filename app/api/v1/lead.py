import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user, require_role
from core.db import get_db
from models.lead import Lead
from models.contact import Contact
from repositories.lead import LeadRepository
from repositories.contact import ContactRepository
from repositories.activity import ActivityRepository
from repositories.task import TaskRepository
from services.lead import LeadService
from services.contact import ContactService
from services.activity import ActivityService
from services.task import TaskService
from services.notification import NotificationService
from repositories.notification import NotificationRepository
from schemas.lead import (
    InquiryCreate,
    LeadAssign,
    LeadCreate,
    LeadRead,
    LeadStatusUpdate,
    LeadUpdate,
    PipelineStat,
)

router = APIRouter(prefix="/leads", tags=["leads"])


def _get_lead_service(session: AsyncSession) -> LeadService:
    return LeadService(LeadRepository(session))


def _get_activity_service(session: AsyncSession) -> ActivityService:
    return ActivityService(ActivityRepository(session))


def _get_task_service(session: AsyncSession) -> TaskService:
    return TaskService(TaskRepository(session))


def _get_notification_service(session: AsyncSession) -> NotificationService:
    return NotificationService(NotificationRepository(session))


@router.post("", response_model=LeadRead, status_code=201)
async def create_lead(
    payload: LeadCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_lead_service(session)
    lead = Lead(**payload.model_dump())
    lead._current_user_id = user.email
    return await service.create(lead)


@router.get("", response_model=List[LeadRead])
async def list_leads(
    status: str | None = None,
    agent_id: uuid.UUID | None = None,
    agency_id: uuid.UUID | None = None,
    contact_id: uuid.UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_lead_service(session)
    if status:
        return await service.list_by_status(status, skip, limit)
    if agent_id:
        return await service.list_by_agent(agent_id, skip, limit)
    if agency_id:
        return await service.list_by_agency(agency_id, skip, limit)
    if contact_id:
        return await service.list_by_contact(contact_id, skip, limit)
    return await service.list(skip, limit)


@router.get("/pipeline", response_model=List[PipelineStat])
async def get_pipeline(
    agency_id: uuid.UUID | None = None,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_lead_service(session)
    return await service.pipeline_stats(agency_id)


@router.get("/{lead_id}", response_model=LeadRead)
async def get_lead(
    lead_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_lead_service(session)
    lead = await service.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=LeadRead)
async def update_lead(
    lead_id: uuid.UUID,
    payload: LeadUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_lead_service(session)
    data = payload.model_dump(exclude_unset=True)
    result = await service.update(lead_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Lead not found")
    return result


@router.patch("/{lead_id}/status", response_model=LeadRead)
async def update_lead_status(
    lead_id: uuid.UUID,
    payload: LeadStatusUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    lead_service = _get_lead_service(session)
    lead = await lead_service.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    old_status = lead.status
    try:
        updated = await lead_service.transition_status(lead_id, payload.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Auto-log activity
    activity_service = _get_activity_service(session)
    await activity_service.log_status_change(
        lead_id=lead_id,
        contact_id=lead.contact_id,
        agent_id=lead.agent_id,
        old_status=old_status,
        new_status=payload.status,
        user_email=user.email,
    )

    # Auto-create follow-up task on "contacted" transition
    if payload.status == "contacted" and lead.agent_id:
        task_service = _get_task_service(session)
        await task_service.create_follow_up(
            lead_id=lead_id,
            contact_id=lead.contact_id,
            assigned_to=user.id,
            assigned_by=user.id,
            days_from_now=3,
            title="Follow-up: lead contacted",
        )

    # Auto-create follow-up on "negotiation" transition
    if payload.status == "negotiation" and lead.agent_id:
        task_service = _get_task_service(session)
        await task_service.create_follow_up(
            lead_id=lead_id,
            contact_id=lead.contact_id,
            assigned_to=user.id,
            assigned_by=user.id,
            days_from_now=7,
            title="Follow-up: negotiation in progress",
        )

    # Notify agent if lead was won
    if payload.status == "won" and lead.agent_id:
        notif_service = _get_notification_service(session)
        from repositories.agent import AgentRepository
        agent_repo = AgentRepository(session)
        agent = await agent_repo.get(lead.agent_id)
        if agent:
            await notif_service.send(
                user_id=agent.user_id,
                title="Lead won!",
                body=f"Congratulations! A lead has been marked as won.",
                notification_type="new_lead",
                reference_type="lead",
                reference_id=lead_id,
            )

    return updated


@router.patch("/{lead_id}/assign", response_model=LeadRead)
async def assign_lead(
    lead_id: uuid.UUID,
    payload: LeadAssign,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    lead_service = _get_lead_service(session)
    lead = await lead_service.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    result = await lead_service.assign_agent(lead_id, payload.agent_id)

    # Auto-log assignment activity
    activity_service = _get_activity_service(session)
    await activity_service.log_assignment(
        lead_id=lead_id,
        contact_id=lead.contact_id,
        agent_id=payload.agent_id,
        user_email=user.email,
    )

    # Notify assigned agent
    notif_service = _get_notification_service(session)
    from repositories.agent import AgentRepository
    agent_repo = AgentRepository(session)
    agent = await agent_repo.get(payload.agent_id)
    if agent:
        await notif_service.send(
            user_id=agent.user_id,
            title="New lead assigned",
            body="A new lead has been assigned to you.",
            notification_type="lead_assigned",
            reference_type="lead",
            reference_id=lead_id,
        )

    return result


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: uuid.UUID,
    user: User = Depends(require_role("admin", "superadmin")),
    session: AsyncSession = Depends(get_db),
):
    service = _get_lead_service(session)
    lead = await service.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    await service.delete(lead_id)


# --- Public inquiry endpoint ---

inquiry_router = APIRouter(tags=["leads"])


@inquiry_router.post("/properties/{property_id}/inquire", response_model=LeadRead, status_code=201)
async def inquire_about_property(
    property_id: uuid.UUID,
    payload: InquiryCreate,
    session: AsyncSession = Depends(get_db),
):
    """Public endpoint: submit an inquiry about a property. Creates Contact + Lead."""
    contact_service = ContactService(ContactRepository(session))
    contact = await contact_service.get_or_create_from_inquiry(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone_number=payload.phone_number,
    )

    # Determine agency from property
    from repositories.property import PropertyRepository
    prop_repo = PropertyRepository(session)
    prop = await prop_repo.get(property_id)
    agency_id = prop.agency_id if prop else None

    lead_service = LeadService(LeadRepository(session))
    lead = Lead(
        contact_id=contact.id,
        property_id=property_id,
        agency_id=agency_id,
        source=payload.source,
        notes=payload.message,
    )
    return await lead_service.create(lead)

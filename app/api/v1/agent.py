import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.agent import Agent
from repositories.agent import AgentRepository
from services.agent import AgentService
from schemas.agent import AgentCreate, AgentRead, AgentUpdate

router = APIRouter(prefix="/agents", tags=["agents"])


def _get_service(session: AsyncSession) -> AgentService:
    return AgentService(AgentRepository(session))


@router.get("", response_model=List[AgentRead])
async def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).list(skip=skip, limit=limit)


@router.get("/{agent_id}", response_model=AgentRead)
async def get_agent(
    agent_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    agent = await _get_service(session).get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.get("/slug/{slug}", response_model=AgentRead)
async def get_agent_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_db),
):
    agent = await _get_service(session).get_by_slug(slug)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.get("/agency/{agency_id}", response_model=List[AgentRead])
async def list_agents_by_agency(
    agency_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).get_by_agency_id(agency_id)


@router.post("", response_model=AgentRead, status_code=201)
async def create_agent(
    payload: AgentCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    obj = Agent(**payload.model_dump())
    setattr(obj, "_current_user_id", user.email)
    return await _get_service(session).create(obj)


@router.patch("/{agent_id}", response_model=AgentRead)
async def update_agent(
    agent_id: uuid.UUID,
    payload: AgentUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    data = payload.model_dump(exclude_unset=True)
    data["_current_user_id"] = user.email
    return await service.update(agent_id, data)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    await service.delete(agent_id)

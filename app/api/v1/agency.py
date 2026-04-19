import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.agency import Agency
from repositories.agency import AgencyRepository
from services.agency import AgencyService
from schemas.agency import AgencyCreate, AgencyRead, AgencyUpdate

router = APIRouter(prefix="/agencies", tags=["agencies"])


def _get_service(session: AsyncSession) -> AgencyService:
    return AgencyService(AgencyRepository(session))


@router.get("", response_model=List[AgencyRead])
async def list_agencies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).list(skip=skip, limit=limit)


@router.get("/{agency_id}", response_model=AgencyRead)
async def get_agency(
    agency_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    agency = await _get_service(session).get(agency_id)
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")
    return agency


@router.get("/country/{country_code}", response_model=List[AgencyRead])
async def list_agencies_by_country(
    country_code: str,
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).get_by_country(country_code)


@router.post("", response_model=AgencyRead, status_code=201)
async def create_agency(
    payload: AgencyCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    obj = Agency(**payload.model_dump())
    setattr(obj, "_current_user_id", user.email)
    return await _get_service(session).create(obj)


@router.patch("/{agency_id}", response_model=AgencyRead)
async def update_agency(
    agency_id: uuid.UUID,
    payload: AgencyUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(agency_id):
        raise HTTPException(status_code=404, detail="Agency not found")
    data = payload.model_dump(exclude_unset=True)
    data["_current_user_id"] = user.email
    return await service.update(agency_id, data)


@router.delete("/{agency_id}", status_code=204)
async def delete_agency(
    agency_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(agency_id):
        raise HTTPException(status_code=404, detail="Agency not found")
    await service.delete(agency_id)

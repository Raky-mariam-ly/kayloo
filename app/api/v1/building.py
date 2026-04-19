import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.building import Building
from repositories.building import BuildingRepository
from services.building import BuildingService
from schemas.building import BuildingCreate, BuildingRead, BuildingUpdate

router = APIRouter(prefix="/buildings", tags=["buildings"])


def _get_service(session: AsyncSession) -> BuildingService:
    return BuildingService(BuildingRepository(session))


@router.get("", response_model=List[BuildingRead])
async def list_buildings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).list(skip=skip, limit=limit)


@router.get("/{building_id}", response_model=BuildingRead)
async def get_building(
    building_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    building = await _get_service(session).get(building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building


@router.get("/slug/{slug}", response_model=BuildingRead)
async def get_building_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_db),
):
    building = await _get_service(session).get_by_slug(slug)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building


@router.get("/agency/{agency_id}", response_model=List[BuildingRead])
async def list_buildings_by_agency(
    agency_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).get_by_agency_id(agency_id)


@router.post("", response_model=BuildingRead, status_code=201)
async def create_building(
    payload: BuildingCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    obj = Building(**payload.model_dump())
    setattr(obj, "_current_user_id", user.email)
    return await _get_service(session).create(obj)


@router.patch("/{building_id}", response_model=BuildingRead)
async def update_building(
    building_id: uuid.UUID,
    payload: BuildingUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(building_id):
        raise HTTPException(status_code=404, detail="Building not found")
    data = payload.model_dump(exclude_unset=True)
    data["_current_user_id"] = user.email
    return await service.update(building_id, data)


@router.delete("/{building_id}", status_code=204)
async def delete_building(
    building_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(building_id):
        raise HTTPException(status_code=404, detail="Building not found")
    await service.delete(building_id)

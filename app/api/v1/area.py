import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.area import Area
from repositories.area import AreaRepository
from services.area import AreaService
from schemas.area import AreaCreate, AreaRead, AreaUpdate

router = APIRouter(prefix="/areas", tags=["areas"])


def _get_service(session: AsyncSession) -> AreaService:
    return AreaService(AreaRepository(session))


@router.get("", response_model=List[AreaRead])
async def list_areas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).list(skip=skip, limit=limit)


@router.get("/{area_id}", response_model=AreaRead)
async def get_area(
    area_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    area = await _get_service(session).get(area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    return area


@router.get("/city/{city_code}", response_model=List[AreaRead])
async def list_areas_by_city(
    city_code: str,
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).get_by_city(city_code)


@router.post("", response_model=AreaRead, status_code=201)
async def create_area(
    payload: AreaCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    obj = Area(**payload.model_dump())
    setattr(obj, "_current_user_id", user.email)
    return await _get_service(session).create(obj)


@router.patch("/{area_id}", response_model=AreaRead)
async def update_area(
    area_id: uuid.UUID,
    payload: AreaUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(area_id):
        raise HTTPException(status_code=404, detail="Area not found")
    data = payload.model_dump(exclude_unset=True)
    data["_current_user_id"] = user.email
    return await service.update(area_id, data)


@router.delete("/{area_id}", status_code=204)
async def delete_area(
    area_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(area_id):
        raise HTTPException(status_code=404, detail="Area not found")
    await service.delete(area_id)

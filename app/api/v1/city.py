import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.city import City
from repositories.city import CityRepository
from services.city import CityService
from schemas.city import CityCreate, CityRead, CityUpdate

router = APIRouter(prefix="/cities", tags=["cities"])


def _get_service(session: AsyncSession) -> CityService:
    return CityService(CityRepository(session))


@router.get("", response_model=List[CityRead])
async def list_cities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).list(skip=skip, limit=limit)


@router.get("/{city_id}", response_model=CityRead)
async def get_city(
    city_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    city = await _get_service(session).get(city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@router.get("/code/{code}", response_model=CityRead)
async def get_city_by_code(
    code: str,
    session: AsyncSession = Depends(get_db),
):
    city = await _get_service(session).get_by_code(code)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@router.get("/country/{country_code}", response_model=List[CityRead])
async def list_cities_by_country(
    country_code: str,
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).get_by_country(country_code)


@router.post("", response_model=CityRead, status_code=201)
async def create_city(
    payload: CityCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    obj = City(**payload.model_dump())
    setattr(obj, "_current_user_id", user.email)
    return await _get_service(session).create(obj)


@router.patch("/{city_id}", response_model=CityRead)
async def update_city(
    city_id: uuid.UUID,
    payload: CityUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(city_id):
        raise HTTPException(status_code=404, detail="City not found")
    data = payload.model_dump(exclude_unset=True)
    data["_current_user_id"] = user.email
    return await service.update(city_id, data)


@router.delete("/{city_id}", status_code=204)
async def delete_city(
    city_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(city_id):
        raise HTTPException(status_code=404, detail="City not found")
    await service.delete(city_id)

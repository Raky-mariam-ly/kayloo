import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.country import Country
from repositories.country import CountryRepository
from services.country import CountryService
from schemas.country import CountryCreate, CountryRead, CountryUpdate

router = APIRouter(prefix="/countries", tags=["countries"])


def _get_service(session: AsyncSession) -> CountryService:
    return CountryService(CountryRepository(session))


@router.get("", response_model=List[CountryRead])
async def list_countries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    return await service.list(skip=skip, limit=limit)


@router.get("/{country_id}", response_model=CountryRead)
async def get_country(
    country_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    country = await service.get(country_id)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country


@router.get("/code/{code}", response_model=CountryRead)
async def get_country_by_code(
    code: str,
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    country = await service.get_by_code(code)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country


@router.post("", response_model=CountryRead, status_code=201)
async def create_country(
    payload: CountryCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    country = Country(**payload.model_dump())
    setattr(country, "_current_user_id", user.email)
    return await service.create(country)


@router.patch("/{country_id}", response_model=CountryRead)
async def update_country(
    country_id: uuid.UUID,
    payload: CountryUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    existing = await service.get(country_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Country not found")
    data = payload.model_dump(exclude_unset=True)
    data["_current_user_id"] = user.email
    return await service.update(country_id, data)


@router.delete("/{country_id}", status_code=204)
async def delete_country(
    country_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    existing = await service.get(country_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Country not found")
    await service.delete(country_id)

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.property import Property
from repositories.property import PropertyRepository
from services.property import PropertyService
from schemas.property import PropertyCreate, PropertyRead, PropertyListRead, PropertyUpdate

router = APIRouter(prefix="/properties", tags=["properties"])


def _get_service(session: AsyncSession) -> PropertyService:
    return PropertyService(PropertyRepository(session))


@router.get("", response_model=List[PropertyListRead])
async def list_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).list(skip=skip, limit=limit)


@router.get("/featured", response_model=List[PropertyListRead])
async def list_featured_properties(
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).get_featured()


@router.get("/status/{status}", response_model=List[PropertyListRead])
async def list_properties_by_status(
    status: str,
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).get_by_status(status)


@router.get("/agency/{agency_id}", response_model=List[PropertyListRead])
async def list_properties_by_agency(
    agency_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).get_by_agency_id(agency_id)


@router.get("/{property_id}", response_model=PropertyRead)
async def get_property(
    property_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    prop = await _get_service(session).get(property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.get("/code/{code}", response_model=PropertyRead)
async def get_property_by_code(
    code: str,
    session: AsyncSession = Depends(get_db),
):
    prop = await _get_service(session).get_by_code(code)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.post("", response_model=PropertyRead, status_code=201)
async def create_property(
    payload: PropertyCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    obj = Property(**payload.model_dump())
    setattr(obj, "_current_user_id", user.email)
    return await _get_service(session).create(obj)


@router.patch("/{property_id}", response_model=PropertyRead)
async def update_property(
    property_id: uuid.UUID,
    payload: PropertyUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(property_id):
        raise HTTPException(status_code=404, detail="Property not found")
    data = payload.model_dump(exclude_unset=True)
    data["_current_user_id"] = user.email
    return await service.update(property_id, data)


@router.delete("/{property_id}", status_code=204)
async def delete_property(
    property_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(property_id):
        raise HTTPException(status_code=404, detail="Property not found")
    await service.delete(property_id)

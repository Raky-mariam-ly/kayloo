import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.property_type import PropertyType
from repositories.property_type import PropertyTypeRepository
from services.property_type import PropertyTypeService
from schemas.property_type import PropertyTypeCreate, PropertyTypeRead, PropertyTypeUpdate

router = APIRouter(prefix="/property-types", tags=["property-types"])


def _get_service(session: AsyncSession) -> PropertyTypeService:
    return PropertyTypeService(PropertyTypeRepository(session))


@router.get("", response_model=List[PropertyTypeRead])
async def list_property_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).list(skip=skip, limit=limit)


@router.get("/{type_id}", response_model=PropertyTypeRead)
async def get_property_type(
    type_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    pt = await _get_service(session).get(type_id)
    if not pt:
        raise HTTPException(status_code=404, detail="Property type not found")
    return pt


@router.get("/code/{code}", response_model=PropertyTypeRead)
async def get_property_type_by_code(
    code: str,
    session: AsyncSession = Depends(get_db),
):
    pt = await _get_service(session).get_by_code(code)
    if not pt:
        raise HTTPException(status_code=404, detail="Property type not found")
    return pt


@router.post("", response_model=PropertyTypeRead, status_code=201)
async def create_property_type(
    payload: PropertyTypeCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    obj = PropertyType(**payload.model_dump())
    setattr(obj, "_current_user_id", user.email)
    return await _get_service(session).create(obj)


@router.patch("/{type_id}", response_model=PropertyTypeRead)
async def update_property_type(
    type_id: uuid.UUID,
    payload: PropertyTypeUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(type_id):
        raise HTTPException(status_code=404, detail="Property type not found")
    data = payload.model_dump(exclude_unset=True)
    data["_current_user_id"] = user.email
    return await service.update(type_id, data)


@router.delete("/{type_id}", status_code=204)
async def delete_property_type(
    type_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(type_id):
        raise HTTPException(status_code=404, detail="Property type not found")
    await service.delete(type_id)

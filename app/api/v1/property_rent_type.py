import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.property_rent_type import PropertyRentType
from repositories.property_rent_type import PropertyRentTypeRepository
from services.property_rent_type import PropertyRentTypeService
from schemas.property_rent_type import PropertyRentTypeCreate, PropertyRentTypeRead, PropertyRentTypeUpdate

router = APIRouter(prefix="/property-rent-types", tags=["property-rent-types"])


def _get_service(session: AsyncSession) -> PropertyRentTypeService:
    return PropertyRentTypeService(PropertyRentTypeRepository(session))


@router.get("", response_model=List[PropertyRentTypeRead])
async def list_property_rent_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).list(skip=skip, limit=limit)


@router.get("/{type_id}", response_model=PropertyRentTypeRead)
async def get_property_rent_type(
    type_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    pt = await _get_service(session).get(type_id)
    if not pt:
        raise HTTPException(status_code=404, detail="Property rent type not found")
    return pt


@router.get("/code/{code}", response_model=PropertyRentTypeRead)
async def get_property_rent_type_by_code(
    code: str,
    session: AsyncSession = Depends(get_db),
):
    pt = await _get_service(session).get_by_code(code)
    if not pt:
        raise HTTPException(status_code=404, detail="Property rent type not found")
    return pt


@router.post("", response_model=PropertyRentTypeRead, status_code=201)
async def create_property_rent_type(
    payload: PropertyRentTypeCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    obj = PropertyRentType(**payload.model_dump())
    setattr(obj, "_current_user_id", user.email)
    return await _get_service(session).create(obj)


@router.patch("/{type_id}", response_model=PropertyRentTypeRead)
async def update_property_rent_type(
    type_id: uuid.UUID,
    payload: PropertyRentTypeUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(type_id):
        raise HTTPException(status_code=404, detail="Property rent type not found")
    data = payload.model_dump(exclude_unset=True)
    data["_current_user_id"] = user.email
    return await service.update(type_id, data)


@router.delete("/{type_id}", status_code=204)
async def delete_property_rent_type(
    type_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(type_id):
        raise HTTPException(status_code=404, detail="Property rent type not found")
    await service.delete(type_id)

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.property_image import PropertyImage
from repositories.property_image import PropertyImageRepository
from services.property_image import PropertyImageService
from schemas.property_image import PropertyImageCreate, PropertyImageRead, PropertyImageUpdate

router = APIRouter(prefix="/property-images", tags=["property-images"])


def _get_service(session: AsyncSession) -> PropertyImageService:
    return PropertyImageService(PropertyImageRepository(session))


@router.get("/property/{property_id}", response_model=List[PropertyImageRead])
async def list_images_by_property(
    property_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).get_by_property_id(property_id)


@router.get("/{image_id}", response_model=PropertyImageRead)
async def get_property_image(
    image_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    img = await _get_service(session).get(image_id)
    if not img:
        raise HTTPException(status_code=404, detail="Property image not found")
    return img


@router.post("", response_model=PropertyImageRead, status_code=201)
async def create_property_image(
    payload: PropertyImageCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    obj = PropertyImage(**payload.model_dump())
    setattr(obj, "_current_user_id", user.email)
    return await _get_service(session).create(obj)


@router.delete("/{image_id}", status_code=204)
async def delete_property_image(
    image_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(image_id):
        raise HTTPException(status_code=404, detail="Property image not found")
    await service.delete(image_id)

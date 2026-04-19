import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.partner import Partner
from repositories.partner import PartnerRepository
from services.partner import PartnerService
from schemas.partner import PartnerCreate, PartnerRead, PartnerUpdate

router = APIRouter(prefix="/partners", tags=["partners"])


def _get_service(session: AsyncSession) -> PartnerService:
    return PartnerService(PartnerRepository(session))


@router.get("", response_model=List[PartnerRead])
async def list_partners(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).list(skip=skip, limit=limit)


@router.get("/{partner_id}", response_model=PartnerRead)
async def get_partner(
    partner_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    partner = await _get_service(session).get(partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner


@router.post("", response_model=PartnerRead, status_code=201)
async def create_partner(
    payload: PartnerCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    obj = Partner(**payload.model_dump())
    setattr(obj, "_current_user_id", user.email)
    return await _get_service(session).create(obj)


@router.patch("/{partner_id}", response_model=PartnerRead)
async def update_partner(
    partner_id: uuid.UUID,
    payload: PartnerUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(partner_id):
        raise HTTPException(status_code=404, detail="Partner not found")
    data = payload.model_dump(exclude_unset=True)
    data["_current_user_id"] = user.email
    return await service.update(partner_id, data)


@router.delete("/{partner_id}", status_code=204)
async def delete_partner(
    partner_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.get(partner_id):
        raise HTTPException(status_code=404, detail="Partner not found")
    await service.delete(partner_id)

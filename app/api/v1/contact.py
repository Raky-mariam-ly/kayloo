import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.contact import Contact
from repositories.contact import ContactRepository
from services.contact import ContactService
from schemas.contact import ContactCreate, ContactRead, ContactUpdate

router = APIRouter(prefix="/contacts", tags=["contacts"])


def _get_service(session: AsyncSession) -> ContactService:
    return ContactService(ContactRepository(session))


@router.post("", response_model=ContactRead, status_code=201)
async def create_contact(
    payload: ContactCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    contact = Contact(**payload.model_dump())
    contact.created_by = user.email
    return await service.create(contact)


@router.get("", response_model=List[ContactRead])
async def list_contacts(
    contact_type: str | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if search:
        return await service.search(search, skip, limit)
    if contact_type:
        return await service.list_by_type(contact_type, skip, limit)
    return await service.list(skip, limit)


@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact(
    contact_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    contact = await service.get(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactRead)
async def update_contact(
    contact_id: uuid.UUID,
    payload: ContactUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    data = payload.model_dump(exclude_unset=True)
    data["updated_by"] = user.email
    result = await service.update(contact_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Contact not found")
    return result


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    contact = await service.get(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    await service.delete(contact_id)

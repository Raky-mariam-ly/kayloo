import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.saved_search import SavedSearch
from repositories.saved_search import SavedSearchRepository
from services.saved_search import SavedSearchService
from schemas.saved_search import SavedSearchCreate, SavedSearchRead, SavedSearchUpdate

router = APIRouter(prefix="/saved-searches", tags=["saved-searches"])


def _get_service(session: AsyncSession) -> SavedSearchService:
    return SavedSearchService(SavedSearchRepository(session))


@router.post("", response_model=SavedSearchRead, status_code=201)
async def create_saved_search(
    payload: SavedSearchCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    saved = SavedSearch(
        user_id=user.id,
        name=payload.name,
        filters=payload.filters,
        notify_enabled=payload.notify_enabled,
    )
    return await service.create(saved)


@router.get("", response_model=List[SavedSearchRead])
async def list_saved_searches(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).list_by_user(user.id)


@router.put("/{search_id}", response_model=SavedSearchRead)
async def update_saved_search(
    search_id: uuid.UUID,
    payload: SavedSearchUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    data = payload.model_dump(exclude_unset=True)
    result = await service.update(search_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Saved search not found")
    return result


@router.delete("/{search_id}", status_code=204)
async def delete_saved_search(
    search_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    s = await service.get(search_id)
    if not s:
        raise HTTPException(status_code=404, detail="Saved search not found")
    await service.delete(search_id)

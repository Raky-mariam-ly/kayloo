import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from repositories.favorite import FavoriteRepository
from services.favorite import FavoriteService
from schemas.favorite import FavoriteRead, FavoriteToggle, FavoriteToggleResponse

router = APIRouter(prefix="/favorites", tags=["favorites"])


def _get_service(session: AsyncSession) -> FavoriteService:
    return FavoriteService(FavoriteRepository(session))


@router.get("", response_model=List[FavoriteRead])
async def list_favorites(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).list_by_user(user.id)


@router.post("/toggle", response_model=FavoriteToggleResponse)
async def toggle_favorite(
    payload: FavoriteToggle,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    return await _get_service(session).toggle(user.id, payload.property_id)


@router.delete("/{property_id}", status_code=204)
async def remove_favorite(
    property_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    removed = await service.repository.delete_by_user_and_property(user.id, property_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Favorite not found")

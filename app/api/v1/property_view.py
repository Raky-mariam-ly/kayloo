import uuid
from typing import List

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from models.property_view import PropertyView
from repositories.property_view import PropertyViewRepository
from services.property_view import PropertyViewService
from schemas.property_view import (
    PropertyViewCount,
    PropertyViewCreate,
    PropertyViewStats,
    TopViewedProperty,
)

router = APIRouter(tags=["property-views"])


def _get_service(session: AsyncSession) -> PropertyViewService:
    return PropertyViewService(PropertyViewRepository(session))


@router.post("/properties/{property_id}/views", status_code=201)
async def record_property_view(
    property_id: uuid.UUID,
    payload: PropertyViewCreate,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Record a property view. Idempotent — one view per session per day."""
    service = _get_service(session)
    view = PropertyView(
        property_id=property_id,
        session_id=payload.session_id,
        country=payload.country,
        city=payload.city,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    result = await service.record_view(view)
    if result is None:
        return {"status": "already_recorded"}
    return {"status": "recorded"}


@router.get("/properties/{property_id}/views/count", response_model=PropertyViewCount)
async def get_property_view_count(
    property_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    total = await service.count_by_property(property_id)
    return PropertyViewCount(property_id=property_id, total=total)


@router.get("/properties/{property_id}/views/stats", response_model=PropertyViewStats)
async def get_property_view_stats(
    property_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    total = await service.count_by_property(property_id)
    by_country = await service.stats_by_country(property_id)
    by_city = await service.stats_by_city(property_id)
    return PropertyViewStats(
        property_id=property_id,
        total=total,
        by_country=by_country,
        by_city=by_city,
    )


@router.get("/analytics/views/top", response_model=List[TopViewedProperty])
async def get_top_viewed_properties(
    limit: int = Query(10, ge=1, le=100),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    """Top viewed properties. Requires authentication."""
    return await _get_service(session).top_viewed(limit)

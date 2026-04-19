import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user, require_role
from core.db import get_db
from models.property_review import PropertyReview
from repositories.property_review import PropertyReviewRepository
from services.property_review import PropertyReviewService
from schemas.property_review import (
    PropertyReviewCreate,
    PropertyReviewRead,
    PropertyReviewUpdate,
    ReviewSummary,
)

router = APIRouter(prefix="/properties/{property_id}/reviews", tags=["property-reviews"])


def _get_service(session: AsyncSession) -> PropertyReviewService:
    return PropertyReviewService(PropertyReviewRepository(session))


@router.get("", response_model=List[PropertyReviewRead])
async def list_approved_reviews(
    property_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List approved reviews for a property."""
    return await _get_service(session).list_approved(property_id, skip, limit)


@router.get("/summary", response_model=ReviewSummary)
async def get_review_summary(
    property_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Average rating, total count, and rating distribution."""
    service = _get_service(session)
    return ReviewSummary(
        property_id=property_id,
        average_rating=await service.average_rating(property_id),
        total_reviews=await service.count_approved(property_id),
        rating_distribution=await service.rating_distribution(property_id),
    )


@router.post("", response_model=PropertyReviewRead, status_code=201)
async def submit_review(
    property_id: uuid.UUID,
    payload: PropertyReviewCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    """Submit or update a review. One review per user per property."""
    service = _get_service(session)
    existing = await service.get_by_user_and_property(user.id, property_id)

    if existing:
        data = payload.model_dump(exclude_unset=True)
        data["_current_user_id"] = user.email
        data["is_approved"] = False  # re-submit requires re-approval
        return await service.update(existing.id, data)

    review = PropertyReview(
        property_id=property_id,
        user_id=user.id,
        rating=payload.rating,
        comment=payload.comment,
    )
    setattr(review, "_current_user_id", user.email)
    return await service.create(review)


@router.delete("", status_code=204)
async def delete_own_review(
    property_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    """Delete the current user's review for this property."""
    service = _get_service(session)
    existing = await service.get_by_user_and_property(user.id, property_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Review not found")
    await service.delete(existing.id)


# --- Admin moderation ---

admin_router = APIRouter(prefix="/reviews", tags=["property-reviews"])


@admin_router.patch("/{review_id}/approve", response_model=PropertyReviewRead)
async def approve_review(
    review_id: uuid.UUID,
    user: User = Depends(require_role("admin", "superadmin")),
    session: AsyncSession = Depends(get_db),
):
    """Approve a review. Admin only."""
    service = _get_service(session)
    review = await service.get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return await service.update(review_id, {"is_approved": True, "_current_user_id": user.email})


@admin_router.patch("/{review_id}/reject", response_model=PropertyReviewRead)
async def reject_review(
    review_id: uuid.UUID,
    user: User = Depends(require_role("admin", "superadmin")),
    session: AsyncSession = Depends(get_db),
):
    """Reject (unapprove) a review. Admin only."""
    service = _get_service(session)
    review = await service.get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return await service.update(review_id, {"is_approved": False, "_current_user_id": user.email})

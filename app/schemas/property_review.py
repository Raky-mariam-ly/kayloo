import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class PropertyReviewRead(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    user_id: uuid.UUID
    rating: int
    comment: str | None = None
    is_approved: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PropertyReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None


class PropertyReviewUpdate(BaseModel):
    rating: int | None = Field(None, ge=1, le=5)
    comment: str | None = None


class ReviewSummary(BaseModel):
    property_id: uuid.UUID
    average_rating: float | None
    total_reviews: int
    rating_distribution: dict[str, int]

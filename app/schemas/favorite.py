import uuid
from datetime import datetime
from pydantic import BaseModel


class FavoriteRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    property_id: uuid.UUID
    created_at: datetime | None

    model_config = {"from_attributes": True}


class FavoriteToggle(BaseModel):
    property_id: uuid.UUID


class FavoriteToggleResponse(BaseModel):
    action: str  # "added" or "removed"
    property_id: str

import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel


class SavedSearchCreate(BaseModel):
    name: str
    filters: dict[str, Any]
    notify_enabled: bool = True


class SavedSearchUpdate(BaseModel):
    name: str | None = None
    filters: dict[str, Any] | None = None
    notify_enabled: bool | None = None


class SavedSearchRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    filters: dict[str, Any]
    notify_enabled: bool
    created_at: datetime | None
    updated_at: datetime | None

    model_config = {"from_attributes": True}

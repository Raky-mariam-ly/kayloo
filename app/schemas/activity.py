import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel


class ActivityCreate(BaseModel):
    lead_id: uuid.UUID | None = None
    contact_id: uuid.UUID | None = None
    property_id: uuid.UUID | None = None
    agent_id: uuid.UUID | None = None
    activity_type: str
    title: str
    description: str | None = None
    metadata_: dict[str, Any] | None = None
    scheduled_at: datetime | None = None


class ActivityRead(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID | None
    contact_id: uuid.UUID | None
    property_id: uuid.UUID | None
    agent_id: uuid.UUID | None
    activity_type: str
    title: str
    description: str | None
    metadata_: dict[str, Any] | None = None
    scheduled_at: datetime | None
    completed_at: datetime | None
    created_at: datetime | None
    created_by: str | None

    model_config = {"from_attributes": True}

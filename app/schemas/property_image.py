import uuid
from datetime import datetime
from pydantic import BaseModel


class PropertyImageRead(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    url: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PropertyImageCreate(BaseModel):
    property_id: uuid.UUID
    url: str


class PropertyImageUpdate(BaseModel):
    url: str | None = None

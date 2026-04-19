import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class AreaRead(BaseModel):
    id: uuid.UUID
    city: str
    name: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class AreaCreate(BaseModel):
    city: str
    name: str = Field(..., min_length=2)
    is_active: bool = False


class AreaUpdate(BaseModel):
    city: str | None = None
    name: str | None = Field(None, min_length=2)
    is_active: bool | None = None

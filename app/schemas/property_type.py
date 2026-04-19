import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class PropertyTypeRead(BaseModel):
    id: uuid.UUID
    code: str
    label: str
    description: str | None = None
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PropertyTypeCreate(BaseModel):
    code: str = Field(..., min_length=2)
    label: str = Field(..., min_length=5)
    description: str | None = None
    is_active: bool = False


class PropertyTypeUpdate(BaseModel):
    code: str | None = Field(None, min_length=2)
    label: str | None = Field(None, min_length=5)
    description: str | None = None
    is_active: bool | None = None

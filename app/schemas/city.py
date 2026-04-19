import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class CityRead(BaseModel):
    id: uuid.UUID
    country: str
    code: str
    name: str | None = None
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class CityCreate(BaseModel):
    country: str
    code: str = Field(..., min_length=2)
    name: str | None = None
    is_active: bool = False


class CityUpdate(BaseModel):
    country: str | None = None
    code: str | None = Field(None, min_length=2)
    name: str | None = None
    is_active: bool | None = None

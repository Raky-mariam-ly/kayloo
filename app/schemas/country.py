import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class CountryRead(BaseModel):
    id: uuid.UUID
    code: str
    name: str | None = None
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class CountryCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=2)
    name: str | None = None
    is_active: bool = False


class CountryUpdate(BaseModel):
    code: str | None = Field(None, min_length=2, max_length=2)
    name: str | None = None
    is_active: bool | None = None

import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class BuildingRead(BaseModel):
    id: uuid.UUID
    agency_id: uuid.UUID | None = None
    city_id: uuid.UUID | None = None
    name: str
    address: str | None = None
    lat: Decimal | None = None
    lng: Decimal | None = None
    slug: str | None = None
    image_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class BuildingCreate(BaseModel):
    agency_id: uuid.UUID | None = None
    city_id: uuid.UUID | None = None
    name: str = Field(..., min_length=1)
    address: str | None = None
    lat: Decimal | None = None
    lng: Decimal | None = None
    slug: str | None = None
    image_url: str | None = None


class BuildingUpdate(BaseModel):
    agency_id: uuid.UUID | None = None
    city_id: uuid.UUID | None = None
    name: str | None = Field(None, min_length=1)
    address: str | None = None
    lat: Decimal | None = None
    lng: Decimal | None = None
    slug: str | None = None
    image_url: str | None = None

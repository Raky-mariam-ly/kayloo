import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class PartnerRead(BaseModel):
    id: uuid.UUID
    country: str
    name: str
    email: str
    phone_number: str
    logo_url: str | None = None
    siteweb_url: str | None = None
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PartnerCreate(BaseModel):
    country: str
    name: str
    email: str
    phone_number: str
    logo_url: str | None = None
    siteweb_url: str | None = None
    is_active: bool = False


class PartnerUpdate(BaseModel):
    country: str | None = None
    name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    logo_url: str | None = None
    siteweb_url: str | None = None
    is_active: bool | None = None

import uuid
from datetime import datetime
from pydantic import BaseModel


class AgencyRead(BaseModel):
    id: uuid.UUID
    country: str
    name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    logo_url: str | None = None
    siteweb_url: str | None = None
    whatsapp_url: str | None = None
    x_url: str | None = None
    facebook_url: str | None = None
    tiktok_url: str | None = None
    youtube_url: str | None = None
    instagram_url: str | None = None
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class AgencyCreate(BaseModel):
    country: str
    name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    logo_url: str | None = None
    siteweb_url: str | None = None
    whatsapp_url: str | None = None
    x_url: str | None = None
    facebook_url: str | None = None
    tiktok_url: str | None = None
    youtube_url: str | None = None
    instagram_url: str | None = None
    is_active: bool = False


class AgencyUpdate(BaseModel):
    country: str | None = None
    name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    logo_url: str | None = None
    siteweb_url: str | None = None
    whatsapp_url: str | None = None
    x_url: str | None = None
    facebook_url: str | None = None
    tiktok_url: str | None = None
    youtube_url: str | None = None
    instagram_url: str | None = None
    is_active: bool | None = None

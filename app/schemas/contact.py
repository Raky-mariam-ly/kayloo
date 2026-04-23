import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone_number: str | None = None
    country: str | None = None
    city: str | None = None
    address: str | None = None
    contact_type: str = "buyer"
    notes: str | None = None


class ContactUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    country: str | None = None
    city: str | None = None
    address: str | None = None
    contact_type: str | None = None
    notes: str | None = None
    is_active: bool | None = None


class ContactRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    first_name: str
    last_name: str
    email: str | None
    phone_number: str | None
    country: str | None
    city: str | None
    address: str | None
    contact_type: str
    notes: str | None
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None

    model_config = {"from_attributes": True}

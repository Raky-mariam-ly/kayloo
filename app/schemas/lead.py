import uuid
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel


class LeadCreate(BaseModel):
    contact_id: uuid.UUID
    property_id: uuid.UUID | None = None
    agent_id: uuid.UUID | None = None
    agency_id: uuid.UUID | None = None
    source: str = "website"
    priority: str = "medium"
    probability: int = 10
    expected_close: date | None = None
    deal_value: Decimal | None = None
    notes: str | None = None


class LeadUpdate(BaseModel):
    property_id: uuid.UUID | None = None
    agent_id: uuid.UUID | None = None
    priority: str | None = None
    probability: int | None = None
    expected_close: date | None = None
    deal_value: Decimal | None = None
    notes: str | None = None
    lost_reason: str | None = None


class LeadRead(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    property_id: uuid.UUID | None
    agent_id: uuid.UUID | None
    agency_id: uuid.UUID | None
    source: str
    status: str
    priority: str
    probability: int
    expected_close: date | None
    deal_value: Decimal | None
    lost_reason: str | None
    notes: str | None
    created_at: datetime | None
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class LeadStatusUpdate(BaseModel):
    status: str


class LeadAssign(BaseModel):
    agent_id: uuid.UUID


class PipelineStat(BaseModel):
    status: str
    count: int


class InquiryCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str | None = None
    message: str | None = None
    source: str = "website"

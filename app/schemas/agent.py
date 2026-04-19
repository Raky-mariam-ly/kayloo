import uuid
from datetime import datetime
from pydantic import BaseModel


class AgentRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    agency_id: uuid.UUID
    slug: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class AgentCreate(BaseModel):
    user_id: uuid.UUID
    agency_id: uuid.UUID
    slug: str | None = None


class AgentUpdate(BaseModel):
    user_id: uuid.UUID | None = None
    agency_id: uuid.UUID | None = None
    slug: str | None = None

import uuid
from datetime import datetime
from pydantic import BaseModel


class TaskCreate(BaseModel):
    lead_id: uuid.UUID | None = None
    contact_id: uuid.UUID | None = None
    property_id: uuid.UUID | None = None
    assigned_to: uuid.UUID
    title: str
    description: str | None = None
    task_type: str = "follow_up"
    priority: str = "medium"
    due_date: datetime


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    task_type: str | None = None
    priority: str | None = None
    status: str | None = None
    due_date: datetime | None = None


class TaskRead(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID | None
    contact_id: uuid.UUID | None
    property_id: uuid.UUID | None
    assigned_to: uuid.UUID
    assigned_by: uuid.UUID | None
    title: str
    description: str | None
    task_type: str
    status: str
    priority: str
    due_date: datetime
    completed_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None

    model_config = {"from_attributes": True}

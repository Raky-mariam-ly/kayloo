import uuid
from datetime import datetime
from pydantic import BaseModel


class NotificationRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    body: str
    notification_type: str
    reference_type: str | None
    reference_id: uuid.UUID | None
    is_read: bool
    created_at: datetime | None

    model_config = {"from_attributes": True}


class UnreadCount(BaseModel):
    count: int

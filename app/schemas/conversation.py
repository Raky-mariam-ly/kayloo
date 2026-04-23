import uuid
from datetime import datetime
from pydantic import BaseModel


class ConversationCreate(BaseModel):
    other_user_id: uuid.UUID
    subject: str | None = None
    property_id: uuid.UUID | None = None
    lead_id: uuid.UUID | None = None


class ConversationRead(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID | None
    lead_id: uuid.UUID | None
    subject: str | None
    is_archived: bool
    created_at: datetime | None
    updated_at: datetime | None
    unread_count: int = 0
    last_message: str | None = None

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    content: str
    message_type: str = "text"
    attachment_url: str | None = None


class MessageRead(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    content: str
    message_type: str
    attachment_url: str | None
    created_at: datetime | None

    model_config = {"from_attributes": True}

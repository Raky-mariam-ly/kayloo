import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text, UUID, func

from core.auth import Base


class Conversation(Base):
    __tablename__ = "conversation"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    property_id = Column(UUID(as_uuid=True), ForeignKey("property_property.id"), nullable=True, index=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("lead.id"), nullable=True)
    subject = Column(Text, nullable=True)
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ConversationParticipant(Base):
    __tablename__ = "conversation_participant"

    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversation.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    last_read_at = Column(DateTime(timezone=True), nullable=True)

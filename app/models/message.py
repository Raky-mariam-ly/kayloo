import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Text, UUID, func

from core.auth import Base


class Message(Base):
    __tablename__ = "message"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversation.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(Text, nullable=False, default="text")  # text, image, document, system
    attachment_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

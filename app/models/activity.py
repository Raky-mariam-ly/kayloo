import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Text, UUID, func
from sqlalchemy.dialects.postgresql import JSON

from core.auth import Base


class Activity(Base):
    __tablename__ = "activity"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("lead.id", ondelete="CASCADE"), nullable=True, index=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contact.id", ondelete="CASCADE"), nullable=True, index=True)
    property_id = Column(UUID(as_uuid=True), ForeignKey("property_property.id"), nullable=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agent.id"), nullable=True)
    activity_type = Column(Text, nullable=False)  # call, email, sms, whatsapp, visit, meeting, note, status_change, document_sent, offer_made, offer_accepted, offer_rejected
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Text, ForeignKey("user.email"), nullable=True)

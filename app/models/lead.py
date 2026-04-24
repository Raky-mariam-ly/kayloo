import uuid
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, Text, UUID, func, event

from core.auth import Base


class Lead(Base):
    __tablename__ = "lead"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contact.id"), nullable=False, index=True)
    property_id = Column(UUID(as_uuid=True), ForeignKey("property_property.id"), nullable=True, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agent.id"), nullable=True, index=True)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agency.id"), nullable=True, index=True)
    source = Column(Text, nullable=False, default="website")  # website, mobile_app, phone, walk_in, referral, social_media
    status = Column(Text, nullable=False, default="new")  # new, contacted, qualified, negotiation, won, lost
    priority = Column(Text, nullable=False, default="medium")  # low, medium, high, urgent
    probability = Column(Integer, nullable=False, default=10)  # 0-100% chance of closing
    expected_close = Column(Date, nullable=True)  # estimated closing date
    deal_value = Column(Numeric(precision=15, scale=2), nullable=True)  # negotiated value (overrides property price)
    lost_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Text, ForeignKey("user.email"), nullable=True)
    updated_by = Column(Text, ForeignKey("user.email"), nullable=True)


@event.listens_for(Lead, "before_insert")
def set_lead_created_by(mapper, connection, target):
    if hasattr(target, '_current_user_id'):
        target.created_by = target._current_user_id


@event.listens_for(Lead, "before_update")
def set_lead_updated_by(mapper, connection, target):
    if hasattr(target, '_current_user_id'):
        target.updated_by = target._current_user_id

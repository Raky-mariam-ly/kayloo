import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Text, UUID, func

from core.auth import Base


class Task(Base):
    __tablename__ = "task"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("lead.id", ondelete="SET NULL"), nullable=True, index=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contact.id", ondelete="SET NULL"), nullable=True, index=True)
    property_id = Column(UUID(as_uuid=True), ForeignKey("property_property.id"), nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(Text, nullable=False, default="follow_up")  # call, email, visit, follow_up, document, other
    status = Column(Text, nullable=False, default="pending")  # pending, in_progress, completed, cancelled
    priority = Column(Text, nullable=False, default="medium")  # low, medium, high, urgent
    due_date = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

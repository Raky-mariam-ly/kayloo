import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text, UUID, func

from core.auth import Base


class Notification(Base):
    __tablename__ = "notification"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    notification_type = Column(Text, nullable=False)  # new_lead, lead_assigned, task_due, task_overdue, new_message, review_posted, saved_search_match, system
    reference_type = Column(Text, nullable=True)  # lead, task, conversation, property
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

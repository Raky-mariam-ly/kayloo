import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text, UUID, func
from sqlalchemy.dialects.postgresql import JSON

from core.auth import Base


class SavedSearch(Base):
    __tablename__ = "saved_search"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(Text, nullable=False)
    filters = Column(JSON, nullable=False)
    notify_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

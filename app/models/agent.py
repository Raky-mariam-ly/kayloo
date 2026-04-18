import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Text, func, UUID

from core.auth import Base


class Agent(Base):
    __tablename__ = "agent"

    id = Column(UUID(as_uuid=True),
                default=uuid.uuid4, primary_key=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agency.id"), nullable=False)
    slug = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Text, ForeignKey("user.email"), nullable=True)
    updated_by = Column(Text, ForeignKey("user.email"), nullable=True)

import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text, func, UUID

from core.auth import Base


class Area(Base):
    __tablename__ = "area"

    id = Column(UUID(as_uuid=True),
                default=uuid.uuid4, primary_key=True, nullable=False)
    city = Column(Text, ForeignKey("city.code"), nullable=False)
    name = Column(Text(), nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Text, ForeignKey("user.email"), nullable=True)
    updated_by = Column(Text, ForeignKey("user.email"), nullable=True)

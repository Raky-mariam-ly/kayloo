import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text, func, UUID

from core.auth import Base


class PropertyRentType(Base):
    __tablename__ = "property_rent_type"

    id = Column(UUID(as_uuid=True),
                default=uuid.uuid4, primary_key=True, nullable=False)
    code = Column(Text(), nullable=False, unique=True)
    label = Column(Text, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Text, ForeignKey("user.email"), nullable=True)
    updated_by = Column(Text, ForeignKey("user.email"), nullable=True)

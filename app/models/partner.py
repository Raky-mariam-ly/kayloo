import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text, func, UUID

from core.auth import Base


class Partner(Base):
    __tablename__ = "partner"

    id = Column(UUID(as_uuid=True),
                default=uuid.uuid4, primary_key=True, nullable=False)
    country = Column(Text, ForeignKey("country.code"), nullable=False)
    name = Column(Text, nullable=False, unique=True)
    email = Column(Text, nullable=False, unique=True)
    phone_number = Column(Text, nullable=False, unique=True)
    logo_url = Column(Text, nullable=True)
    siteweb_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Text, ForeignKey("user.email"), nullable=True)
    updated_by = Column(Text, ForeignKey("user.email"), nullable=True)

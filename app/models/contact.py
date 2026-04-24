import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text, UUID, func

from core.auth import Base


class Contact(Base):
    __tablename__ = "contact"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True, index=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    email = Column(Text, nullable=True, index=True)
    phone_number = Column(Text, nullable=True)
    country = Column(Text, ForeignKey("country.code"), nullable=True)
    city = Column(Text, ForeignKey("city.code"), nullable=True)
    address = Column(Text, nullable=True)
    contact_type = Column(Text, nullable=False, default="buyer")  # buyer, seller, tenant, landlord, investor
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Text, ForeignKey("user.email"), nullable=True)
    updated_by = Column(Text, ForeignKey("user.email"), nullable=True)

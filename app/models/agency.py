import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text, func, UUID
from sqlalchemy.orm import relationship
from sqlalchemy_file import FileField as FileStorageField

from core.auth import Base


class Agency(Base):
    __tablename__ = "agency"

    id = Column(UUID(as_uuid=True),
                default=uuid.uuid4, primary_key=True, nullable=False)
    country = Column(Text, ForeignKey("country.code"), nullable=False)
    name = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    phone_number = Column(Text, nullable=True)
    logo_url = Column(FileStorageField(upload_storage="images"), nullable=True)
    siteweb_url = Column(Text, nullable=True)
    whatsapp_url = Column(Text, nullable=True)
    x_url = Column(Text, nullable=True)
    facebook_url = Column(Text, nullable=True)
    tiktok_url = Column(Text, nullable=True)
    youtube_url = Column(Text, nullable=True)
    instagram_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Text, ForeignKey("user.email"), nullable=True)
    updated_by = Column(Text, ForeignKey("user.email"), nullable=True)

    agents = relationship("Agent", back_populates="agency", lazy="selectin")
    properties = relationship("Property", back_populates="agency",
                              foreign_keys="Property.agency_id", lazy="selectin")

import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Text, func, UUID
from sqlalchemy.orm import relationship
from sqlalchemy_file import FileField as FileStorageField

from core.auth import Base


class PropertyImage(Base):
    __tablename__ = "property_image"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    property_id = Column(UUID(as_uuid=True), ForeignKey("property_property.id"), nullable=False)
    url = Column(FileStorageField(upload_storage="images"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Text, ForeignKey("user.email"), nullable=True)
    updated_by = Column(Text, ForeignKey("user.email"), nullable=True)

    property = relationship("Property", back_populates="images")

import uuid
from sqlalchemy import Column, DateTime, ForeignKey, UUID, func
from sqlalchemy.orm import relationship
from sqlalchemy_file import FileField as FileStorageField

from core.auth import Base


class PropertyGallery(Base):
    __tablename__ = "property_gallery"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    property_id = Column(
        UUID(as_uuid=True),
        ForeignKey("property_property.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    images = Column(FileStorageField(upload_storage="images", multiple=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    property = relationship("Property", back_populates="gallery")

import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Numeric, Text, func, UUID
from sqlalchemy_file import FileField as FileStorageField

from core.auth import Base


class Building(Base):
    __tablename__ = "building"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agency.id"), nullable=True)
    city_id = Column(UUID(as_uuid=True), ForeignKey("city.id"), nullable=True)
    name = Column(Text, nullable=False)
    address = Column(Text, nullable=True)
    lat = Column(Numeric(21, 6), nullable=True)
    lng = Column(Numeric(21, 6), nullable=True)
    slug = Column(Text, nullable=True)
    image_url = Column(FileStorageField(upload_storage="images"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Text, ForeignKey("user.email"), nullable=True)
    updated_by = Column(Text, ForeignKey("user.email"), nullable=True)

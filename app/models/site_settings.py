from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy_file import FileField as FileStorageField

from core.auth import Base


class SiteSettings(Base):
    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, default=1)
    logo_url = Column(FileStorageField(upload_storage="images", extra={"acl": "public-read"}), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

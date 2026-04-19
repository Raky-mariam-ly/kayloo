import uuid
from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, Text, UUID, func

from core.auth import Base


class PropertyView(Base):
    __tablename__ = "property_view"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    property_id = Column(UUID(as_uuid=True), ForeignKey("property_property.id"), nullable=False, index=True)
    viewer_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    session_id = Column(Text, nullable=False)
    view_date = Column(Date, server_default=func.current_date(), nullable=False)
    country = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    ip_address = Column(Text, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_property_view_dedup", "property_id", "session_id", "view_date", unique=True),
        Index("ix_property_view_country", "property_id", "country"),
    )

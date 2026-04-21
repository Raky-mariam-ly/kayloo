import uuid
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, UUID, func

from core.auth import Base


class Favorite(Base):
    __tablename__ = "favorite"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    property_id = Column(UUID(as_uuid=True), ForeignKey("property_property.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "property_id", name="uq_favorite_user_property"),
    )

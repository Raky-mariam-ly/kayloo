import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func, UUID
from sqlalchemy import event

from core.auth import Base


class PropertyReview(Base):
    __tablename__ = "property_review"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    property_id = Column(UUID(as_uuid=True), ForeignKey("property_property.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    is_approved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Text, ForeignKey("user.email"), nullable=True)
    updated_by = Column(Text, ForeignKey("user.email"), nullable=True)

    __table_args__ = (
        UniqueConstraint("property_id", "user_id", name="uq_property_review_user"),
    )


@event.listens_for(PropertyReview, "before_insert")
def set_created_by(mapper, connection, target):
    if hasattr(target, '_current_user_id'):
        target.created_by = target._current_user_id


@event.listens_for(PropertyReview, "before_update")
def set_updated_by(mapper, connection, target):
    if hasattr(target, '_current_user_id'):
        target.updated_by = target._current_user_id

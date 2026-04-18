import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text, func, UUID
from sqlalchemy import event
from core.auth import Base, current_active_user


class Country(Base):
    __tablename__ = "country"

    id = Column(UUID(as_uuid=True),
                default=uuid.uuid4, primary_key=True, nullable=False)
    code = Column(Text(), nullable=False, unique=True)
    name = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Text, ForeignKey("user.email"), nullable=True)
    updated_by = Column(Text, ForeignKey("user.email"), nullable=True)


@event.listens_for(Country, "before_insert")
def set_created_by(mapper, connection, target):
    # Accessing user ID here requires a global context or passing it to the object
    if hasattr(target, '_current_user_id'):
        target.created_by = target._current_user_id


@event.listens_for(Country, "before_update")
def set_updated_by(mapper, connection, target):
    if hasattr(target, '_current_user_id'):
        target.updated_by = target._current_user_id

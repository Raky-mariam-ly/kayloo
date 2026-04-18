import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, Text, func, UUID
from sqlalchemy.orm import relationship

from core.auth import Base


class Property(Base):
    __tablename__ = "property_property"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    building_id = Column(UUID(as_uuid=True), nullable=True)
    owner_id = Column(UUID(as_uuid=True), nullable=True)
    agency_id = Column(UUID(as_uuid=True), ForeignKey("agency.id"), nullable=True)
    label = Column(Text, nullable=True)
    code = Column(Text, nullable=True)
    status_before_reserved = Column(Text, nullable=True)
    managed_by = Column(Text, nullable=True)
    base_price_type = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    sale_account_code = Column(Text, nullable=True)
    usage = Column(Text, nullable=True)
    type = Column(Text, nullable=True)
    status = Column(Text, nullable=True)
    rent_type = Column(Text, nullable=True)
    rental_period = Column(Text, nullable=True)
    tag = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    level = Column(Text, nullable=True)
    position = Column(Text, nullable=True)
    apartment_number = Column(Text, nullable=True)
    country = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    street = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    zone = Column(Text, nullable=True)
    bath_room_count = Column(Integer, nullable=True)
    bed_room_count = Column(Integer, nullable=True)
    kitchen_count = Column(Integer, nullable=True)
    living_room_count = Column(Integer, nullable=True)
    build_year = Column(Text, nullable=True)
    lng = Column(Numeric(21, 6), nullable=True)
    lat = Column(Numeric(21, 6), nullable=True)
    acquisition_date = Column(Date, nullable=True)
    acquisition_price = Column(Numeric(21, 6), nullable=True)
    acquisition_fee = Column(Numeric(21, 6), nullable=True)
    surface = Column(Numeric(21, 6), nullable=True)
    free_since = Column(Date, nullable=True)
    currency = Column(Text, nullable=True)
    vat_rate = Column(Numeric(21, 6), nullable=True)
    tom_rate = Column(Numeric(21, 6), nullable=True)
    ir_rate = Column(Numeric(21, 6), nullable=True)
    mgmt_rate = Column(Numeric(21, 6), nullable=True)
    commission_rate = Column(Numeric(21, 6), nullable=True)
    deposit_rate = Column(Numeric(21, 6), nullable=True)
    sale_price = Column(Numeric(21, 6), nullable=True)
    price = Column(Numeric(21, 6), nullable=True)
    base_price = Column(Numeric(21, 6), nullable=True)
    extra_price = Column(Numeric(21, 6), nullable=True)
    rent_price = Column(Numeric(21, 6), nullable=True)
    syndic_amount = Column(Numeric(21, 6), nullable=True)
    is_featured = Column(Boolean, nullable=True)
    is_hidden = Column(Boolean, default=False, nullable=False)
    is_exposed = Column(Boolean, default=False, nullable=False)
    is_saleable = Column(Boolean, default=True, nullable=False)
    is_managed = Column(Boolean, default=False, nullable=False)
    archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Text, ForeignKey("user.email"), nullable=True)
    updated_by = Column(Text, ForeignKey("user.email"), nullable=True)

    images = relationship(
        "PropertyImage",
        back_populates="property",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

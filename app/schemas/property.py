import uuid
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel


class PropertyImageNested(BaseModel):
    id: uuid.UUID
    url: str

    model_config = {"from_attributes": True}


class PropertyRead(BaseModel):
    id: uuid.UUID
    version: int
    building_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    agency_id: uuid.UUID | None = None
    label: str | None = None
    code: str | None = None
    status: str | None = None
    type: str | None = None
    usage: str | None = None
    rent_type: str | None = None
    rental_period: str | None = None
    managed_by: str | None = None
    base_price_type: str | None = None
    description: str | None = None
    image_url: str | None = None
    country: str | None = None
    city: str | None = None
    zone: str | None = None
    street: str | None = None
    address: str | None = None
    level: str | None = None
    position: str | None = None
    apartment_number: str | None = None
    surface: Decimal | None = None
    bed_room_count: int | None = None
    bath_room_count: int | None = None
    kitchen_count: int | None = None
    living_room_count: int | None = None
    build_year: str | None = None
    lat: Decimal | None = None
    lng: Decimal | None = None
    currency: str | None = None
    price: Decimal | None = None
    base_price: Decimal | None = None
    extra_price: Decimal | None = None
    sale_price: Decimal | None = None
    rent_price: Decimal | None = None
    syndic_amount: Decimal | None = None
    vat_rate: Decimal | None = None
    tom_rate: Decimal | None = None
    ir_rate: Decimal | None = None
    mgmt_rate: Decimal | None = None
    commission_rate: Decimal | None = None
    deposit_rate: Decimal | None = None
    is_featured: bool | None = None
    is_hidden: bool
    is_exposed: bool
    is_saleable: bool
    is_managed: bool
    archived: bool
    images: list[PropertyImageNested] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PropertyListRead(BaseModel):
    """Lighter schema for list endpoints."""
    id: uuid.UUID
    label: str | None = None
    code: str | None = None
    status: str | None = None
    type: str | None = None
    country: str | None = None
    city: str | None = None
    price: Decimal | None = None
    currency: str | None = None
    surface: Decimal | None = None
    bed_room_count: int | None = None
    image_url: str | None = None
    is_featured: bool | None = None
    is_hidden: bool
    archived: bool

    model_config = {"from_attributes": True}


class PropertyCreate(BaseModel):
    building_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    agency_id: uuid.UUID | None = None
    label: str | None = None
    code: str | None = None
    status: str | None = None
    type: str | None = None
    usage: str | None = None
    rent_type: str | None = None
    rental_period: str | None = None
    managed_by: str | None = None
    base_price_type: str | None = None
    description: str | None = None
    image_url: str | None = None
    country: str | None = None
    city: str | None = None
    zone: str | None = None
    street: str | None = None
    address: str | None = None
    level: str | None = None
    position: str | None = None
    apartment_number: str | None = None
    surface: Decimal | None = None
    bed_room_count: int | None = None
    bath_room_count: int | None = None
    kitchen_count: int | None = None
    living_room_count: int | None = None
    build_year: str | None = None
    lat: Decimal | None = None
    lng: Decimal | None = None
    acquisition_date: date | None = None
    acquisition_price: Decimal | None = None
    acquisition_fee: Decimal | None = None
    free_since: date | None = None
    currency: str | None = None
    price: Decimal | None = None
    base_price: Decimal | None = None
    extra_price: Decimal | None = None
    sale_price: Decimal | None = None
    rent_price: Decimal | None = None
    syndic_amount: Decimal | None = None
    vat_rate: Decimal | None = None
    tom_rate: Decimal | None = None
    ir_rate: Decimal | None = None
    mgmt_rate: Decimal | None = None
    commission_rate: Decimal | None = None
    deposit_rate: Decimal | None = None
    is_featured: bool | None = None
    is_hidden: bool = False
    is_exposed: bool = False
    is_saleable: bool = True
    is_managed: bool = False
    archived: bool = False


class PropertyUpdate(BaseModel):
    building_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    agency_id: uuid.UUID | None = None
    label: str | None = None
    code: str | None = None
    status: str | None = None
    type: str | None = None
    usage: str | None = None
    rent_type: str | None = None
    rental_period: str | None = None
    managed_by: str | None = None
    base_price_type: str | None = None
    description: str | None = None
    image_url: str | None = None
    country: str | None = None
    city: str | None = None
    zone: str | None = None
    street: str | None = None
    address: str | None = None
    level: str | None = None
    position: str | None = None
    apartment_number: str | None = None
    surface: Decimal | None = None
    bed_room_count: int | None = None
    bath_room_count: int | None = None
    kitchen_count: int | None = None
    living_room_count: int | None = None
    build_year: str | None = None
    lat: Decimal | None = None
    lng: Decimal | None = None
    acquisition_date: date | None = None
    acquisition_price: Decimal | None = None
    acquisition_fee: Decimal | None = None
    free_since: date | None = None
    currency: str | None = None
    price: Decimal | None = None
    base_price: Decimal | None = None
    extra_price: Decimal | None = None
    sale_price: Decimal | None = None
    rent_price: Decimal | None = None
    syndic_amount: Decimal | None = None
    vat_rate: Decimal | None = None
    tom_rate: Decimal | None = None
    ir_rate: Decimal | None = None
    mgmt_rate: Decimal | None = None
    commission_rate: Decimal | None = None
    deposit_rate: Decimal | None = None
    is_featured: bool | None = None
    is_hidden: bool | None = None
    is_exposed: bool | None = None
    is_saleable: bool | None = None
    is_managed: bool | None = None
    archived: bool | None = None

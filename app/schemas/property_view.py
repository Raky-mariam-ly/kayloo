import uuid
from pydantic import BaseModel


class PropertyViewCreate(BaseModel):
    session_id: str
    country: str | None = None
    city: str | None = None


class PropertyViewCount(BaseModel):
    property_id: uuid.UUID
    total: int


class CountryStat(BaseModel):
    country: str | None
    count: int


class CityStat(BaseModel):
    country: str | None
    city: str | None
    count: int


class PropertyViewStats(BaseModel):
    property_id: uuid.UUID
    total: int
    by_country: list[CountryStat]
    by_city: list[CityStat]


class TopViewedProperty(BaseModel):
    property_id: str
    count: int

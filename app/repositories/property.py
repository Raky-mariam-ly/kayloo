from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from models.property import Property
from repositories.base import BaseRepository

RENT_TYPES = ("RENT_EMPTY", "RENT_FURNISHED")
SALE_TYPES = ("SALE",)


class PropertyRepository(BaseRepository[Property]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Property)

    async def get_by_code(self, code: str) -> Optional[Property]:
        result = await self.db.execute(select(self.model).filter_by(code=code))
        return result.scalar_one_or_none()

    async def get_by_agency_id(self, agency_id: UUID) -> List[Property]:
        result = await self.db.execute(select(self.model).filter_by(agency_id=agency_id))
        return result.scalars().all()

    async def get_by_agency(self, agency_id: UUID, exclude_hidden: bool = True) -> List[Property]:
        query = select(self.model).where(self.model.agency_id == agency_id)
        if exclude_hidden:
            query = query.where(
                self.model.is_hidden.is_(False),
                self.model.archived.is_(False),
            )
        query = query.order_by(self.model.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_status(self, status: str) -> List[Property]:
        result = await self.db.execute(select(self.model).filter_by(status=status))
        return result.scalars().all()

    async def get_featured(self) -> List[Property]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.is_featured.is_(True),
                self.model.is_hidden.is_(False),
                self.model.archived.is_(False),
            )
        )
        return result.scalars().all()

    def _apply_search_filters(self, query, city, type, price_min, price_max, is_featured, rent_category):
        if city:
            query = query.where(self.model.city.ilike(f"%{city}%"))
        if type:
            query = query.where(self.model.type.ilike(f"%{type}%"))
        if price_min is not None:
            query = query.where(self.model.price >= price_min)
        if price_max is not None:
            query = query.where(self.model.price <= price_max)
        if is_featured is not None:
            query = query.where(self.model.is_featured.is_(is_featured))
        if rent_category == "rent":
            query = query.where(self.model.rent_type.in_(RENT_TYPES))
        elif rent_category == "sale":
            query = query.where(self.model.rent_type.in_(SALE_TYPES))
        return query

    async def search(
        self,
        city: Optional[str] = None,
        type: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        is_featured: Optional[bool] = None,
        rent_category: Optional[str] = None,
        skip: int = 0,
        limit: int = 12,
    ) -> List[Property]:
        query = select(self.model).where(
            self.model.is_hidden.is_(False),
            self.model.archived.is_(False),
        )
        query = self._apply_search_filters(query, city, type, price_min, price_max, is_featured, rent_category)
        query = query.order_by(self.model.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_distinct_cities(self) -> List[str]:
        result = await self.db.execute(
            select(distinct(self.model.city))
            .where(
                self.model.city.isnot(None),
                self.model.city != "",
                self.model.is_hidden.is_(False),
                self.model.archived.is_(False),
            )
            .order_by(self.model.city)
        )
        return [row[0] for row in result.fetchall()]

    async def count_search(
        self,
        city: Optional[str] = None,
        type: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        is_featured: Optional[bool] = None,
        rent_category: Optional[str] = None,
    ) -> int:
        query = select(func.count(self.model.id)).where(
            self.model.is_hidden.is_(False),
            self.model.archived.is_(False),
        )
        query = self._apply_search_filters(query, city, type, price_min, price_max, is_featured, rent_category)
        result = await self.db.execute(query)
        return result.scalar_one()
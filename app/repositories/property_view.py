from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.property_view import PropertyView
from repositories.base import BaseRepository


class PropertyViewRepository(BaseRepository[PropertyView]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PropertyView)

    async def exists_today(self, property_id: UUID, session_id: str) -> bool:
        result = await self.db.execute(
            select(func.count(self.model.id)).filter_by(
                property_id=property_id,
                session_id=session_id,
                view_date=func.current_date(),
            )
        )
        return result.scalar_one() > 0

    async def count_by_property(self, property_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(self.model.id)).filter_by(property_id=property_id)
        )
        return result.scalar_one()

    async def stats_by_country(self, property_id: UUID) -> List[Dict[str, Any]]:
        query = (
            select(
                self.model.country,
                func.count(self.model.id).label("count"),
            )
            .filter_by(property_id=property_id)
            .group_by(self.model.country)
            .order_by(func.count(self.model.id).desc())
        )
        result = await self.db.execute(query)
        return [{"country": row.country, "count": row.count} for row in result.all()]

    async def stats_by_city(self, property_id: UUID) -> List[Dict[str, Any]]:
        query = (
            select(
                self.model.country,
                self.model.city,
                func.count(self.model.id).label("count"),
            )
            .filter_by(property_id=property_id)
            .group_by(self.model.country, self.model.city)
            .order_by(func.count(self.model.id).desc())
        )
        result = await self.db.execute(query)
        return [{"country": row.country, "city": row.city, "count": row.count} for row in result.all()]

    async def top_viewed(self, limit: int = 10) -> List[Dict[str, Any]]:
        query = (
            select(
                self.model.property_id,
                func.count(self.model.id).label("count"),
            )
            .group_by(self.model.property_id)
            .order_by(func.count(self.model.id).desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return [{"property_id": str(row.property_id), "count": row.count} for row in result.all()]

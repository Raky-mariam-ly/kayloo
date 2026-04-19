from typing import Any, Dict, List
from uuid import UUID

from models.property_view import PropertyView
from repositories.property_view import PropertyViewRepository
from services.base import BaseService


class PropertyViewService(BaseService[PropertyView]):
    def __init__(self, repository: PropertyViewRepository):
        super().__init__(repository)

    async def record_view(self, view: PropertyView) -> PropertyView | None:
        """Record a view if not already recorded today for this session."""
        if await self.repository.exists_today(view.property_id, view.session_id):
            return None
        return await self.repository.create(view)

    async def count_by_property(self, property_id: UUID) -> int:
        return await self.repository.count_by_property(property_id)

    async def stats_by_country(self, property_id: UUID) -> List[Dict[str, Any]]:
        return await self.repository.stats_by_country(property_id)

    async def stats_by_city(self, property_id: UUID) -> List[Dict[str, Any]]:
        return await self.repository.stats_by_city(property_id)

    async def top_viewed(self, limit: int = 10) -> List[Dict[str, Any]]:
        return await self.repository.top_viewed(limit)

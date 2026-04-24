from typing import List
from uuid import UUID

from models.favorite import Favorite
from repositories.favorite import FavoriteRepository
from services.base import BaseService


class FavoriteService(BaseService[Favorite]):
    def __init__(self, repository: FavoriteRepository):
        super().__init__(repository)

    async def list_by_user(self, user_id: UUID) -> List[Favorite]:
        return await self.repository.list_by_user(user_id)

    async def toggle(self, user_id: UUID, property_id: UUID) -> dict:
        """Add favorite if not exists, remove if exists. Returns action taken."""
        existing = await self.repository.get_by_user_and_property(user_id, property_id)
        if existing:
            await self.repository.delete_by_user_and_property(user_id, property_id)
            return {"action": "removed", "property_id": str(property_id)}
        fav = Favorite(user_id=user_id, property_id=property_id)
        await self.repository.create(fav)
        return {"action": "added", "property_id": str(property_id)}

    async def is_favorite(self, user_id: UUID, property_id: UUID) -> bool:
        existing = await self.repository.get_by_user_and_property(user_id, property_id)
        return existing is not None

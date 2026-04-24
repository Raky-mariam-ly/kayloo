from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from repositories.base import BaseRepository


class FavoriteRepository(BaseRepository[Favorite]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Favorite)

    async def list_by_user(self, user_id: UUID) -> List[Favorite]:
        result = await self.db.execute(
            select(self.model)
            .filter_by(user_id=user_id)
            .order_by(self.model.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_user_and_property(self, user_id: UUID, property_id: UUID) -> Optional[Favorite]:
        result = await self.db.execute(
            select(self.model).filter_by(user_id=user_id, property_id=property_id)
        )
        return result.scalar_one_or_none()

    async def delete_by_user_and_property(self, user_id: UUID, property_id: UUID) -> bool:
        fav = await self.get_by_user_and_property(user_id, property_id)
        if fav:
            await self.db.delete(fav)
            await self.db.commit()
            return True
        return False

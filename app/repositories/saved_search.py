from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.saved_search import SavedSearch
from repositories.base import BaseRepository


class SavedSearchRepository(BaseRepository[SavedSearch]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SavedSearch)

    async def list_by_user(self, user_id: UUID) -> List[SavedSearch]:
        result = await self.db.execute(
            select(self.model)
            .filter_by(user_id=user_id)
            .order_by(self.model.created_at.desc())
        )
        return result.scalars().all()

    async def list_with_notifications(self) -> List[SavedSearch]:
        result = await self.db.execute(
            select(self.model).filter_by(notify_enabled=True)
        )
        return result.scalars().all()

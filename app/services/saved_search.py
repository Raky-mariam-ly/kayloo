from typing import List
from uuid import UUID

from models.saved_search import SavedSearch
from repositories.saved_search import SavedSearchRepository
from services.base import BaseService


class SavedSearchService(BaseService[SavedSearch]):
    def __init__(self, repository: SavedSearchRepository):
        super().__init__(repository)

    async def list_by_user(self, user_id: UUID) -> List[SavedSearch]:
        return await self.repository.list_by_user(user_id)

    async def list_with_notifications(self) -> List[SavedSearch]:
        return await self.repository.list_with_notifications()

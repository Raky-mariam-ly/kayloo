from typing import List, Optional
from uuid import UUID

from models.agent import Agent
from repositories.agent import AgentRepository
from services.base import BaseService


class AgentService(BaseService[Agent]):
    def __init__(self, repository: AgentRepository):
        super().__init__(repository)

    async def get_by_slug(self, slug: str) -> Optional[Agent]:
        return await self.repository.get_by_slug(slug)

    async def get_by_user_id(self, user_id: UUID) -> Optional[Agent]:
        return await self.repository.get_by_user_id(user_id)

    async def get_by_agency_id(self, agency_id: UUID) -> List[Agent]:
        return await self.repository.get_by_agency_id(agency_id)

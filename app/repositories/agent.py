from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.agent import Agent
from repositories.base import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Agent)

    async def get_by_slug(self, slug: str) -> Optional[Agent]:
        result = await self.db.execute(select(self.model).filter_by(slug=slug))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> Optional[Agent]:
        result = await self.db.execute(select(self.model).filter_by(user_id=user_id))
        return result.scalar_one_or_none()

    async def get_by_agency_id(self, agency_id: UUID) -> List[Agent]:
        result = await self.db.execute(select(self.model).filter_by(agency_id=agency_id))
        return result.scalars().all()

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.building import Building
from repositories.base import BaseRepository


class BuildingRepository(BaseRepository[Building]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Building)

    async def get_by_slug(self, slug: str) -> Optional[Building]:
        result = await self.db.execute(select(self.model).filter_by(slug=slug))
        return result.scalar_one_or_none()

    async def get_by_agency_id(self, agency_id: UUID) -> List[Building]:
        result = await self.db.execute(select(self.model).filter_by(agency_id=agency_id))
        return result.scalars().all()

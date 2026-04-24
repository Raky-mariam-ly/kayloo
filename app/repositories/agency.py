from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.agency import Agency
from repositories.base import BaseRepository


class AgencyRepository(BaseRepository[Agency]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Agency)

    async def get_by_country(self, country: str) -> List[Agency]:
        result = await self.db.execute(select(self.model).filter_by(country=country))
        return result.scalars().all()

    async def get_active(self) -> List[Agency]:
        result = await self.db.execute(
            select(self.model)
            .where(self.model.is_active == True)
            .order_by(self.model.name)
        )
        return result.scalars().all()

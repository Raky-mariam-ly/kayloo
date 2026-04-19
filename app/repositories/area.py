from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.area import Area
from repositories.base import BaseRepository


class AreaRepository(BaseRepository[Area]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Area)

    async def get_by_city(self, city: str) -> List[Area]:
        result = await self.db.execute(select(self.model).filter_by(city=city))
        return result.scalars().all()

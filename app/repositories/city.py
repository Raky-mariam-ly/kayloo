from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.city import City
from repositories.base import BaseRepository


class CityRepository(BaseRepository[City]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, City)

    async def get_by_code(self, code: str) -> Optional[City]:
        result = await self.db.execute(select(self.model).filter_by(code=code))
        return result.scalar_one_or_none()

    async def get_by_country(self, country: str) -> List[City]:
        result = await self.db.execute(select(self.model).filter_by(country=country))
        return result.scalars().all()

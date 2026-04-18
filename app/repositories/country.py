from sqlalchemy.ext.asyncio import AsyncSession
from alembic.environment import Optional

from models.country import Country
from repositories.base import BaseRepository


class CountryRepository(BaseRepository[Country]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Country)

    async def get_by_code(self, code: str) -> Optional[Country]:
        result = await self.db.execute(self.model.select().filter_by(code=code))
        return result.scalar_one_or_none()

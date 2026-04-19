from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.property_type import PropertyType
from repositories.base import BaseRepository


class PropertyTypeRepository(BaseRepository[PropertyType]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PropertyType)

    async def get_by_code(self, code: str) -> Optional[PropertyType]:
        result = await self.db.execute(select(self.model).filter_by(code=code))
        return result.scalar_one_or_none()

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.property_rent_type import PropertyRentType
from repositories.base import BaseRepository


class PropertyRentTypeRepository(BaseRepository[PropertyRentType]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PropertyRentType)

    async def get_by_code(self, code: str) -> Optional[PropertyRentType]:
        result = await self.db.execute(select(self.model).filter_by(code=code))
        return result.scalar_one_or_none()

from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.property_image import PropertyImage
from repositories.base import BaseRepository


class PropertyImageRepository(BaseRepository[PropertyImage]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PropertyImage)

    async def get_by_property_id(self, property_id: UUID) -> List[PropertyImage]:
        result = await self.db.execute(select(self.model).filter_by(property_id=property_id))
        return result.scalars().all()

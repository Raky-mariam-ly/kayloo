from typing import List
from uuid import UUID

from models.property_image import PropertyImage
from repositories.property_image import PropertyImageRepository
from services.base import BaseService


class PropertyImageService(BaseService[PropertyImage]):
    def __init__(self, repository: PropertyImageRepository):
        super().__init__(repository)

    async def get_by_property_id(self, property_id: UUID) -> List[PropertyImage]:
        return await self.repository.get_by_property_id(property_id)

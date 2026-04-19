from typing import Optional

from models.property_type import PropertyType
from repositories.property_type import PropertyTypeRepository
from services.base import BaseService


class PropertyTypeService(BaseService[PropertyType]):
    def __init__(self, repository: PropertyTypeRepository):
        super().__init__(repository)

    async def get_by_code(self, code: str) -> Optional[PropertyType]:
        return await self.repository.get_by_code(code)

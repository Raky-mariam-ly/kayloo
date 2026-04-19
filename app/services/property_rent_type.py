from typing import Optional

from models.property_rent_type import PropertyRentType
from repositories.property_rent_type import PropertyRentTypeRepository
from services.base import BaseService


class PropertyRentTypeService(BaseService[PropertyRentType]):
    def __init__(self, repository: PropertyRentTypeRepository):
        super().__init__(repository)

    async def get_by_code(self, code: str) -> Optional[PropertyRentType]:
        return await self.repository.get_by_code(code)

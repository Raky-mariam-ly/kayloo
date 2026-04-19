from typing import List, Optional
from uuid import UUID

from models.property import Property
from repositories.property import PropertyRepository
from services.base import BaseService


class PropertyService(BaseService[Property]):
    def __init__(self, repository: PropertyRepository):
        super().__init__(repository)

    async def get_by_code(self, code: str) -> Optional[Property]:
        return await self.repository.get_by_code(code)

    async def get_by_agency_id(self, agency_id: UUID) -> List[Property]:
        return await self.repository.get_by_agency_id(agency_id)

    async def get_by_status(self, status: str) -> List[Property]:
        return await self.repository.get_by_status(status)

    async def get_featured(self) -> List[Property]:
        return await self.repository.get_featured()

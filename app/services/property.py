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

    async def search(
        self,
        city: Optional[str] = None,
        type: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        skip: int = 0,
        limit: int = 12,
    ) -> List[Property]:
        return await self.repository.search(
            city=city, type=type,
            price_min=price_min, price_max=price_max,
            skip=skip, limit=limit,
        )

    async def count_search(
        self,
        city: Optional[str] = None,
        type: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
    ) -> int:
        return await self.repository.count_search(
            city=city, type=type,
            price_min=price_min, price_max=price_max,
        )

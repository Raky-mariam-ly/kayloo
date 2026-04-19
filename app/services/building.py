from typing import List, Optional
from uuid import UUID

from models.building import Building
from repositories.building import BuildingRepository
from services.base import BaseService


class BuildingService(BaseService[Building]):
    def __init__(self, repository: BuildingRepository):
        super().__init__(repository)

    async def get_by_slug(self, slug: str) -> Optional[Building]:
        return await self.repository.get_by_slug(slug)

    async def get_by_agency_id(self, agency_id: UUID) -> List[Building]:
        return await self.repository.get_by_agency_id(agency_id)

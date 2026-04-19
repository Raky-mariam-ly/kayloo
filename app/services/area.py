from typing import List

from models.area import Area
from repositories.area import AreaRepository
from services.base import BaseService


class AreaService(BaseService[Area]):
    def __init__(self, repository: AreaRepository):
        super().__init__(repository)

    async def get_by_city(self, city: str) -> List[Area]:
        return await self.repository.get_by_city(city)

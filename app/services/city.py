from typing import List

from models.city import City
from repositories.city import CityRepository
from services.base import BaseService


class CityService(BaseService[City]):
    def __init__(self, repository: CityRepository):
        super().__init__(repository)

    async def get_by_code(self, code: str) -> City:
        return await self.repository.get_by_code(code)

    async def get_by_country(self, country: str) -> List[City]:
        return await self.repository.get_by_country(country)

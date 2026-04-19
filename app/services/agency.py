from typing import List

from models.agency import Agency
from repositories.agency import AgencyRepository
from services.base import BaseService


class AgencyService(BaseService[Agency]):
    def __init__(self, repository: AgencyRepository):
        super().__init__(repository)

    async def get_by_country(self, country: str) -> List[Agency]:
        return await self.repository.get_by_country(country)

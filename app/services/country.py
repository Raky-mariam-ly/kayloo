

from models.country import Country
from repositories.country import CountryRepository
from services.base import BaseService


class CountryService(BaseService[Country]):
    def __init__(self, repository: CountryRepository):
        super().__init__(repository)

    async def get_by_code(self, code: str) -> Country:
        return await self.repository.get_by_code(code)

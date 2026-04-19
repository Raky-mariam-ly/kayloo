from typing import Optional

from models.partner import Partner
from repositories.partner import PartnerRepository
from services.base import BaseService


class PartnerService(BaseService[Partner]):
    def __init__(self, repository: PartnerRepository):
        super().__init__(repository)

    async def get_by_name(self, name: str) -> Optional[Partner]:
        return await self.repository.get_by_name(name)

    async def get_by_email(self, email: str) -> Optional[Partner]:
        return await self.repository.get_by_email(email)

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.partner import Partner
from repositories.base import BaseRepository


class PartnerRepository(BaseRepository[Partner]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Partner)

    async def get_by_name(self, name: str) -> Optional[Partner]:
        result = await self.db.execute(select(self.model).filter_by(name=name))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Partner]:
        result = await self.db.execute(select(self.model).filter_by(email=email))
        return result.scalar_one_or_none()

    async def get_active(self):
        result = await self.db.execute(
            select(self.model)
            .where(self.model.is_active.is_(True))
            .order_by(self.model.name)
        )
        return result.scalars().all()

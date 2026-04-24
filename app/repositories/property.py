from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.property import Property
from repositories.base import BaseRepository


class PropertyRepository(BaseRepository[Property]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Property)

    async def get_by_code(self, code: str) -> Optional[Property]:
        result = await self.db.execute(select(self.model).filter_by(code=code))
        return result.scalar_one_or_none()

    async def get_by_agency_id(self, agency_id: UUID) -> List[Property]:
        result = await self.db.execute(select(self.model).filter_by(agency_id=agency_id))
        return result.scalars().all()

    async def get_by_agency(self, agency_id: UUID, exclude_hidden: bool = True) -> List[Property]:
        query = select(self.model).where(self.model.agency_id == agency_id)
        if exclude_hidden:
            query = query.where(
                self.model.is_hidden.is_(False),
                self.model.archived.is_(False),
            )
        query = query.order_by(self.model.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_status(self, status: str) -> List[Property]:
        result = await self.db.execute(select(self.model).filter_by(status=status))
        return result.scalars().all()

    async def get_featured(self) -> List[Property]:
        result = await self.db.execute(select(self.model).filter_by(is_featured=True))
        return result.scalars().all()

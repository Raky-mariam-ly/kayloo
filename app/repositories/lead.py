from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import func, or_, select, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_admin.contrib.sqla.helpers import build_query

from models.lead import Lead
from repositories.base import BaseRepository


class LeadRepository(BaseRepository[Lead]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Lead)

    async def list_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Lead]:
        result = await self.db.execute(
            select(self.model).filter_by(status=status).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def list_by_agent(self, agent_id: UUID, skip: int = 0, limit: int = 100) -> List[Lead]:
        result = await self.db.execute(
            select(self.model).filter_by(agent_id=agent_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def list_by_agency(self, agency_id: UUID, skip: int = 0, limit: int = 100,
                             where: Union[Dict[str, Any], str, None] = None,
                             order_by: Optional[List[str]] = None) -> List[Lead]:
        query = select(self.model).filter(self.model.agency_id == agency_id)
        if where is not None:
            query = query.filter(self._get_search_query(where)) if isinstance(
                where, str) else build_query(where, self.model)
        if order_by:
            for order in order_by:
                query = query.order_by(order)
        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def count_by_agency(self, agency_id: UUID,
                              where: Union[Dict[str, Any], str, None] = None) -> int:
        query = select(func.count(self.model.id)).filter(self.model.agency_id == agency_id)
        if where is not None:
            query = query.filter(self._get_search_query(where)) if isinstance(
                where, str) else build_query(where, self.model)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def list_by_contact(self, contact_id: UUID, skip: int = 0, limit: int = 100) -> List[Lead]:
        result = await self.db.execute(
            select(self.model).filter_by(contact_id=contact_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def count_by_status(self) -> List[Dict[str, Any]]:
        result = await self.db.execute(
            select(
                self.model.status,
                func.count(self.model.id).label("count"),
            ).group_by(self.model.status)
        )
        return [{"status": row.status, "count": row.count} for row in result.all()]

    async def pipeline_stats(self, agency_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        query = select(
            self.model.status,
            func.count(self.model.id).label("count"),
        )
        if agency_id:
            query = query.filter_by(agency_id=agency_id)
        query = query.group_by(self.model.status)
        result = await self.db.execute(query)
        return [{"status": row.status, "count": row.count} for row in result.all()]

from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_admin.contrib.sqla.helpers import build_query

from models.activity import Activity
from models.lead import Lead
from repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Activity)

    def _agency_subquery(self, agency_id: UUID):
        """Activities linked to leads in the given agency."""
        return self.model.lead_id.in_(
            select(Lead.id).filter(Lead.agency_id == agency_id)
        )

    async def list_by_agency(self, agency_id: UUID, skip: int = 0, limit: int = 100,
                             where: Union[Dict[str, Any], str, None] = None,
                             order_by: Optional[List[str]] = None) -> List[Activity]:
        query = select(self.model).filter(self._agency_subquery(agency_id))
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
        query = select(func.count(self.model.id)).filter(self._agency_subquery(agency_id))
        if where is not None:
            query = query.filter(self._get_search_query(where)) if isinstance(
                where, str) else build_query(where, self.model)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def list_by_lead(self, lead_id: UUID, skip: int = 0, limit: int = 50) -> List[Activity]:
        result = await self.db.execute(
            select(self.model)
            .filter_by(lead_id=lead_id)
            .order_by(self.model.created_at.desc())
            .offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def list_by_contact(self, contact_id: UUID, skip: int = 0, limit: int = 50) -> List[Activity]:
        result = await self.db.execute(
            select(self.model)
            .filter_by(contact_id=contact_id)
            .order_by(self.model.created_at.desc())
            .offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def list_by_agent(self, agent_id: UUID, skip: int = 0, limit: int = 50) -> List[Activity]:
        result = await self.db.execute(
            select(self.model)
            .filter_by(agent_id=agent_id)
            .order_by(self.model.created_at.desc())
            .offset(skip).limit(limit)
        )
        return result.scalars().all()

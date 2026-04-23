from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_admin.contrib.sqla.helpers import build_query

from models.task import Task
from models.lead import Lead
from repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Task)

    def _agency_subquery(self, agency_id: UUID):
        """Tasks linked to leads in the given agency."""
        return self.model.lead_id.in_(
            select(Lead.id).filter(Lead.agency_id == agency_id)
        )

    async def list_by_agency(self, agency_id: UUID, skip: int = 0, limit: int = 100,
                             where: Union[Dict[str, Any], str, None] = None,
                             order_by: Optional[List[str]] = None) -> List[Task]:
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

    async def list_by_assignee(self, user_id: UUID, skip: int = 0, limit: int = 50) -> List[Task]:
        result = await self.db.execute(
            select(self.model)
            .filter_by(assigned_to=user_id)
            .order_by(self.model.due_date.asc())
            .offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def list_by_status(self, user_id: UUID, status: str) -> List[Task]:
        result = await self.db.execute(
            select(self.model)
            .filter_by(assigned_to=user_id, status=status)
            .order_by(self.model.due_date.asc())
        )
        return result.scalars().all()

    async def list_overdue(self, user_id: UUID) -> List[Task]:
        result = await self.db.execute(
            select(self.model)
            .filter(
                self.model.assigned_to == user_id,
                self.model.status.in_(["pending", "in_progress"]),
                self.model.due_date < func.now(),
            )
            .order_by(self.model.due_date.asc())
        )
        return result.scalars().all()

    async def list_by_lead(self, lead_id: UUID) -> List[Task]:
        result = await self.db.execute(
            select(self.model)
            .filter_by(lead_id=lead_id)
            .order_by(self.model.due_date.asc())
        )
        return result.scalars().all()

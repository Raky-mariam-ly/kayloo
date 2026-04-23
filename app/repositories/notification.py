from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_admin.contrib.sqla.helpers import build_query

from models.notification import Notification
from models.agent import Agent
from repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Notification)

    def _agency_subquery(self, agency_id: UUID):
        """Notifications for users who are agents of the given agency."""
        return self.model.user_id.in_(
            select(Agent.user_id).filter(Agent.agency_id == agency_id)
        )

    async def list_by_agency(self, agency_id: UUID, skip: int = 0, limit: int = 100,
                             where: Union[Dict[str, Any], str, None] = None,
                             order_by: Optional[List[str]] = None) -> List[Notification]:
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

    async def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 50) -> List[Notification]:
        result = await self.db.execute(
            select(self.model)
            .filter_by(user_id=user_id)
            .order_by(self.model.created_at.desc())
            .offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def unread_count(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(self.model.id)).filter_by(user_id=user_id, is_read=False)
        )
        return result.scalar_one()

    async def mark_read(self, notification_id: UUID) -> None:
        await self.db.execute(
            update(self.model).where(self.model.id == notification_id).values(is_read=True)
        )
        await self.db.commit()

    async def mark_all_read(self, user_id: UUID) -> int:
        result = await self.db.execute(
            update(self.model)
            .where(self.model.user_id == user_id, self.model.is_read == False)
            .values(is_read=True)
        )
        await self.db.commit()
        return result.rowcount

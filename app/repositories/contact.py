from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_admin.contrib.sqla.helpers import build_query

from models.contact import Contact
from models.lead import Lead
from repositories.base import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Contact)

    def _agency_subquery(self, agency_id: UUID):
        """Contacts that have at least one lead in the given agency."""
        return self.model.id.in_(
            select(Lead.contact_id).filter(Lead.agency_id == agency_id)
        )

    async def list_by_agency(self, agency_id: UUID, skip: int = 0, limit: int = 100,
                             where: Union[Dict[str, Any], str, None] = None,
                             order_by: Optional[List[str]] = None) -> List[Contact]:
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

    async def get_by_email(self, email: str) -> Optional[Contact]:
        result = await self.db.execute(
            select(self.model).filter_by(email=email)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> Optional[Contact]:
        result = await self.db.execute(
            select(self.model).filter_by(user_id=user_id)
        )
        return result.scalar_one_or_none()

    async def list_by_type(self, contact_type: str, skip: int = 0, limit: int = 100) -> List[Contact]:
        result = await self.db.execute(
            select(self.model).filter_by(contact_type=contact_type).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def search(self, term: str, skip: int = 0, limit: int = 100) -> List[Contact]:
        result = await self.db.execute(
            select(self.model).filter(self._get_search_query(term)).offset(skip).limit(limit)
        )
        return result.scalars().all()

import logging
from typing import Any, Dict, Generic, TypeVar, Type, List, Optional, Union
from sqlalchemy import func, func, or_, select, Text, String
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_admin.contrib.sqla.helpers import build_query
from abc import ABC, abstractmethod


T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
    @abstractmethod
    def create(self, entity: T) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: any, data: Dict[str, Any]) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: any) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    async def count(self, where: Union[Dict[str, Any], str, None] = None) -> int:
        raise NotImplementedError

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100, where: Union[Dict[str, Any], str, None] = None, order_by: Optional[List[str]] = None) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: any) -> None:
        raise NotImplementedError


class BaseRepository(AbstractRepository[T]):
    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db
        self.model = model

    def _get_search_query(self, term: str) -> Any:
        """
        Return SQLAlchemy whereclause to use for full text search

        Args:
           term: Filtering term
        Returns:
            SQLAlchemy whereclause to use for full text search
        """
        # 1. Identify all string-based columns dynamically
        search_columns = [
            column for column in self.model.__table__.columns
            if isinstance(column.type, (String, Text)) and column.name not in ["created_by", "updated_by"]
        ]

        # 2. Create 'ilike' conditions for each column
        search_term_fmt = f"%{term}%"
        conditions = [
            getattr(self.model, col.name).ilike(search_term_fmt)
            for col in search_columns
        ]
        return or_(*conditions)

    async def create(self, entity: T) -> Optional[T]:
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update(self, id: any, data: Dict[str, Any]) -> Optional[T]:
        obj = await self.get(id)
        if obj is None:
            return None
        for key, value in data.items():
            setattr(obj, key, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get(self, id: any) -> Optional[T]:
        result = await self.db.execute(select(self.model).filter_by(id=id))
        return result.scalar_one_or_none()

    async def count(self, where: Union[Dict[str, Any], str, None] = None) -> int:
        query = select(func.count(self.model.id))
        logging.info(f"BaseRepository.count: where={where}")
        if where is not None:
            query = query.filter(self._get_search_query(where)) if isinstance(
                where, str) else build_query(where, self.model)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def list(self, skip: int = 0, limit: int = 100, where: Union[Dict[str, Any], str, None] = None, order_by: Optional[List[str]] = None) -> List[T]:
        query = select(self.model)
        if where is not None:
            query = query.filter(self._get_search_query(where)) if isinstance(
                where, str) else build_query(where, self.model)
        if order_by is not None:
            for order in order_by:
                query = query.order_by(order)
        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def delete(self, id: any) -> None:
        obj = await self.get(id)
        if obj is not None:
            await self.db.delete(obj)
            await self.db.commit()

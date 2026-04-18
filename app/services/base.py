import logging
from typing import Generic, Optional, Optional, TypeVar

from repositories.base import AbstractRepository, BaseRepository


T = TypeVar("T")

logger = logging.getLogger(__name__)


class BaseService(Generic[T]):
    def __init__(self, repository: AbstractRepository[T]):
        self.repository = repository

    async def create(self, entity: T) -> Optional[T]:
        logger.info(f"Creating entity: {entity}")
        return await self.repository.create(entity)

    async def update(self, id: any, data: dict) -> Optional[T]:
        logger.info(f"Updating entity with id: {id}, data: {data}")
        return await self.repository.update(id, data)

    async def get(self, id: any) -> Optional[T]:
        logger.info(f"Getting entity by id: {id}")
        return await self.repository.get(id)

    async def count(self, where: dict = None) -> int:
        logger.info(f"Counting entities with filter: {where}")
        return await self.repository.count(where)

    async def list(self, skip: int = 0, limit: int = 100, where: dict = None, order_by: list = None) -> list[T]:
        logger.info(
            f"Listing entities with skip: {skip}, limit: {limit}, filter: {where}, order_by: {order_by}")
        return await self.repository.list(skip, limit, where, order_by)

    async def delete(self, id: any) -> None:
        logger.info(f"Deleting entity with id: {id}")
        await self.repository.delete(id)

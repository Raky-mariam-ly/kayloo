from typing import Any, Dict, List, Optional
from uuid import UUID

from models.property_review import PropertyReview
from repositories.property_review import PropertyReviewRepository
from services.base import BaseService


class PropertyReviewService(BaseService[PropertyReview]):
    def __init__(self, repository: PropertyReviewRepository):
        super().__init__(repository)

    async def get_by_user_and_property(self, user_id: UUID, property_id: UUID) -> Optional[PropertyReview]:
        return await self.repository.get_by_user_and_property(user_id, property_id)

    async def list_approved(self, property_id: UUID, skip: int = 0, limit: int = 50) -> List[PropertyReview]:
        return await self.repository.list_approved(property_id, skip, limit)

    async def count_approved(self, property_id: UUID) -> int:
        return await self.repository.count_approved(property_id)

    async def average_rating(self, property_id: UUID) -> Optional[float]:
        return await self.repository.average_rating(property_id)

    async def rating_distribution(self, property_id: UUID) -> Dict[str, int]:
        return await self.repository.rating_distribution(property_id)

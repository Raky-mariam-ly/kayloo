from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import case, cast, func, Integer, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.property_review import PropertyReview
from repositories.base import BaseRepository


class PropertyReviewRepository(BaseRepository[PropertyReview]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PropertyReview)

    async def get_by_user_and_property(self, user_id: UUID, property_id: UUID) -> Optional[PropertyReview]:
        result = await self.db.execute(
            select(self.model).filter_by(user_id=user_id, property_id=property_id)
        )
        return result.scalar_one_or_none()

    async def list_approved(self, property_id: UUID, skip: int = 0, limit: int = 50) -> List[PropertyReview]:
        result = await self.db.execute(
            select(self.model)
            .filter_by(property_id=property_id, is_approved=True)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def count_approved(self, property_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(self.model.id))
            .filter_by(property_id=property_id, is_approved=True)
        )
        return result.scalar_one()

    async def average_rating(self, property_id: UUID) -> Optional[float]:
        result = await self.db.execute(
            select(func.avg(self.model.rating))
            .filter_by(property_id=property_id, is_approved=True)
        )
        avg = result.scalar_one()
        return round(float(avg), 1) if avg is not None else None

    async def rating_distribution(self, property_id: UUID) -> Dict[str, int]:
        query = select(
            *[
                func.count(case((self.model.rating == i, 1))).label(f"r{i}")
                for i in range(1, 6)
            ]
        ).filter_by(property_id=property_id, is_approved=True)
        result = await self.db.execute(query)
        row = result.one()
        return {str(i): getattr(row, f"r{i}") for i in range(1, 6)}

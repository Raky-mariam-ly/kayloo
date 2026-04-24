"""
Agency-scoping utilities.

All CRM data is scoped to the current user's agency (resolved via the Agent entity).
Users without an Agent record are blocked from CRM features.
"""

from uuid import UUID
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_agency_id(session: AsyncSession, user) -> Optional[UUID]:
    """Resolve the agency_id for a user via the Agent table.

    Returns None if the user is not linked to any agency.
    """
    from models.agent import Agent
    result = await session.execute(
        select(Agent.agency_id).filter_by(user_id=user.id).limit(1)
    )
    return result.scalar_one_or_none()

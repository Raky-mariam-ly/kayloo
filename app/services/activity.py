from typing import List
from uuid import UUID

from models.activity import Activity
from repositories.activity import ActivityRepository
from services.base import BaseService


class ActivityService(BaseService[Activity]):
    def __init__(self, repository: ActivityRepository):
        super().__init__(repository)

    async def list_by_lead(self, lead_id: UUID, skip: int = 0, limit: int = 50) -> List[Activity]:
        return await self.repository.list_by_lead(lead_id, skip, limit)

    async def list_by_contact(self, contact_id: UUID, skip: int = 0, limit: int = 50) -> List[Activity]:
        return await self.repository.list_by_contact(contact_id, skip, limit)

    async def list_by_agent(self, agent_id: UUID, skip: int = 0, limit: int = 50) -> List[Activity]:
        return await self.repository.list_by_agent(agent_id, skip, limit)

    async def log_status_change(self, lead_id: UUID, contact_id: UUID, agent_id: UUID,
                                 old_status: str, new_status: str, user_email: str = None) -> Activity:
        activity = Activity(
            lead_id=lead_id,
            contact_id=contact_id,
            agent_id=agent_id,
            activity_type="status_change",
            title=f"Status changed: {old_status} → {new_status}",
            metadata_={"old_status": old_status, "new_status": new_status},
        )
        if user_email:
            activity.created_by = user_email
        return await self.repository.create(activity)

    async def log_assignment(self, lead_id: UUID, contact_id: UUID, agent_id: UUID,
                              user_email: str = None) -> Activity:
        activity = Activity(
            lead_id=lead_id,
            contact_id=contact_id,
            agent_id=agent_id,
            activity_type="note",
            title=f"Lead assigned to agent",
            metadata_={"agent_id": str(agent_id)},
        )
        if user_email:
            activity.created_by = user_email
        return await self.repository.create(activity)

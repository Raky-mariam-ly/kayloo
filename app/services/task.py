from datetime import timedelta
from typing import List
from uuid import UUID

from sqlalchemy import func

from models.task import Task
from repositories.task import TaskRepository
from services.base import BaseService


class TaskService(BaseService[Task]):
    def __init__(self, repository: TaskRepository):
        super().__init__(repository)

    async def list_by_assignee(self, user_id: UUID, skip: int = 0, limit: int = 50) -> List[Task]:
        return await self.repository.list_by_assignee(user_id, skip, limit)

    async def list_by_status(self, user_id: UUID, status: str) -> List[Task]:
        return await self.repository.list_by_status(user_id, status)

    async def list_overdue(self, user_id: UUID) -> List[Task]:
        return await self.repository.list_overdue(user_id)

    async def list_by_lead(self, lead_id: UUID) -> List[Task]:
        return await self.repository.list_by_lead(lead_id)

    async def complete(self, task_id: UUID) -> Task | None:
        return await self.repository.update(task_id, {
            "status": "completed",
            "completed_at": func.now(),
        })

    async def create_follow_up(self, lead_id: UUID, contact_id: UUID,
                                assigned_to: UUID, assigned_by: UUID,
                                days_from_now: int = 3, title: str = None) -> Task:
        """Auto-create a follow-up task for a lead."""
        from datetime import datetime, timezone
        task = Task(
            lead_id=lead_id,
            contact_id=contact_id,
            assigned_to=assigned_to,
            assigned_by=assigned_by,
            title=title or "Follow-up on lead",
            task_type="follow_up",
            priority="medium",
            due_date=datetime.now(timezone.utc) + timedelta(days=days_from_now),
        )
        return await self.repository.create(task)

from typing import List
from uuid import UUID

from models.notification import Notification
from repositories.notification import NotificationRepository
from services.base import BaseService


class NotificationService(BaseService[Notification]):
    def __init__(self, repository: NotificationRepository):
        super().__init__(repository)

    async def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 50) -> List[Notification]:
        return await self.repository.list_by_user(user_id, skip, limit)

    async def unread_count(self, user_id: UUID) -> int:
        return await self.repository.unread_count(user_id)

    async def mark_read(self, notification_id: UUID) -> None:
        return await self.repository.mark_read(notification_id)

    async def mark_all_read(self, user_id: UUID) -> int:
        return await self.repository.mark_all_read(user_id)

    async def send(self, user_id: UUID, title: str, body: str,
                   notification_type: str, reference_type: str = None,
                   reference_id: UUID = None) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            body=body,
            notification_type=notification_type,
            reference_type=reference_type,
            reference_id=reference_id,
        )
        return await self.repository.create(notification)

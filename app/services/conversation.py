from typing import List, Optional
from uuid import UUID

from models.conversation import Conversation
from models.message import Message
from repositories.conversation import ConversationRepository, MessageRepository
from services.base import BaseService


class ConversationService(BaseService[Conversation]):
    def __init__(self, conversation_repo: ConversationRepository, message_repo: MessageRepository):
        super().__init__(conversation_repo)
        self.message_repo = message_repo

    async def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 50) -> List[Conversation]:
        return await self.repository.list_by_user(user_id, skip, limit)

    async def start_conversation(self, creator_id: UUID, other_user_id: UUID,
                                  subject: str = None, property_id: UUID = None,
                                  lead_id: UUID = None) -> Conversation:
        conversation = Conversation(
            property_id=property_id,
            lead_id=lead_id,
            subject=subject,
        )
        conversation = await self.repository.create(conversation)
        await self.repository.add_participant(conversation.id, creator_id)
        await self.repository.add_participant(conversation.id, other_user_id)
        return conversation

    async def is_participant(self, conversation_id: UUID, user_id: UUID) -> bool:
        return await self.repository.is_participant(conversation_id, user_id)

    async def send_message(self, conversation_id: UUID, sender_id: UUID,
                            content: str, message_type: str = "text",
                            attachment_url: str = None) -> Message:
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            attachment_url=attachment_url,
        )
        message = await self.message_repo.create(message)
        # Update conversation updated_at
        await self.repository.update(conversation_id, {})
        return message

    async def get_messages(self, conversation_id: UUID, skip: int = 0, limit: int = 50) -> List[Message]:
        return await self.message_repo.list_by_conversation(conversation_id, skip, limit)

    async def mark_read(self, conversation_id: UUID, user_id: UUID) -> None:
        await self.repository.mark_read(conversation_id, user_id)

    async def unread_count(self, conversation_id: UUID, user_id: UUID) -> int:
        return await self.repository.unread_count(conversation_id, user_id)

    async def last_message(self, conversation_id: UUID) -> Optional[Message]:
        return await self.message_repo.last_message(conversation_id)

    async def archive(self, conversation_id: UUID) -> Optional[Conversation]:
        return await self.repository.update(conversation_id, {"is_archived": True})

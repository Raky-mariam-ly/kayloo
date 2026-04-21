from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_admin.contrib.sqla.helpers import build_query

from models.conversation import Conversation, ConversationParticipant
from models.lead import Lead
from models.message import Message
from repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversation)

    def _agency_subquery(self, agency_id: UUID):
        """Conversations linked to leads in the given agency."""
        return self.model.lead_id.in_(
            select(Lead.id).filter(Lead.agency_id == agency_id)
        )

    async def list_by_agency(self, agency_id: UUID, skip: int = 0, limit: int = 100,
                             where: Union[Dict[str, Any], str, None] = None,
                             order_by: Optional[List[str]] = None) -> List[Conversation]:
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

    async def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 50) -> List[Conversation]:
        result = await self.db.execute(
            select(Conversation)
            .join(ConversationParticipant, ConversationParticipant.conversation_id == Conversation.id)
            .filter(ConversationParticipant.user_id == user_id)
            .filter(Conversation.is_archived == False)
            .order_by(Conversation.updated_at.desc())
            .offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def add_participant(self, conversation_id: UUID, user_id: UUID) -> None:
        participant = ConversationParticipant(
            conversation_id=conversation_id,
            user_id=user_id,
        )
        self.db.add(participant)
        await self.db.commit()

    async def is_participant(self, conversation_id: UUID, user_id: UUID) -> bool:
        result = await self.db.execute(
            select(ConversationParticipant).filter_by(
                conversation_id=conversation_id, user_id=user_id
            )
        )
        return result.scalar_one_or_none() is not None

    async def mark_read(self, conversation_id: UUID, user_id: UUID) -> None:
        result = await self.db.execute(
            select(ConversationParticipant).filter_by(
                conversation_id=conversation_id, user_id=user_id
            )
        )
        participant = result.scalar_one_or_none()
        if participant:
            participant.last_read_at = func.now()
            await self.db.commit()

    async def unread_count(self, conversation_id: UUID, user_id: UUID) -> int:
        """Count messages in conversation sent after user's last_read_at."""
        part_result = await self.db.execute(
            select(ConversationParticipant).filter_by(
                conversation_id=conversation_id, user_id=user_id
            )
        )
        participant = part_result.scalar_one_or_none()
        if not participant or not participant.last_read_at:
            result = await self.db.execute(
                select(func.count(Message.id)).filter(
                    Message.conversation_id == conversation_id,
                    Message.sender_id != user_id,
                )
            )
            return result.scalar_one()

        result = await self.db.execute(
            select(func.count(Message.id)).filter(
                Message.conversation_id == conversation_id,
                Message.sender_id != user_id,
                Message.created_at > participant.last_read_at,
            )
        )
        return result.scalar_one()


class MessageRepository(BaseRepository[Message]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Message)

    async def list_by_conversation(self, conversation_id: UUID, skip: int = 0, limit: int = 50) -> List[Message]:
        result = await self.db.execute(
            select(self.model)
            .filter_by(conversation_id=conversation_id)
            .order_by(self.model.created_at.desc())
            .offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def last_message(self, conversation_id: UUID) -> Optional[Message]:
        result = await self.db.execute(
            select(self.model)
            .filter_by(conversation_id=conversation_id)
            .order_by(self.model.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

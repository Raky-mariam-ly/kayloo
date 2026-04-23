import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user
from core.db import get_db
from repositories.conversation import ConversationRepository, MessageRepository
from services.conversation import ConversationService
from schemas.conversation import ConversationCreate, ConversationRead, MessageCreate, MessageRead

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _get_service(session: AsyncSession) -> ConversationService:
    return ConversationService(
        ConversationRepository(session),
        MessageRepository(session),
    )


@router.post("", response_model=ConversationRead, status_code=201)
async def start_conversation(
    payload: ConversationCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    conversation = await service.start_conversation(
        creator_id=user.id,
        other_user_id=payload.other_user_id,
        subject=payload.subject,
        property_id=payload.property_id,
        lead_id=payload.lead_id,
    )
    return ConversationRead(
        id=conversation.id,
        property_id=conversation.property_id,
        lead_id=conversation.lead_id,
        subject=conversation.subject,
        is_archived=conversation.is_archived,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        unread_count=0,
    )


@router.get("", response_model=List[ConversationRead])
async def list_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    conversations = await service.list_by_user(user.id, skip, limit)
    result = []
    for conv in conversations:
        unread = await service.unread_count(conv.id, user.id)
        last_msg = await service.last_message(conv.id)
        result.append(ConversationRead(
            id=conv.id,
            property_id=conv.property_id,
            lead_id=conv.lead_id,
            subject=conv.subject,
            is_archived=conv.is_archived,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            unread_count=unread,
            last_message=last_msg.content if last_msg else None,
        ))
    return result


@router.get("/{conversation_id}/messages", response_model=List[MessageRead])
async def list_messages(
    conversation_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.is_participant(conversation_id, user.id):
        raise HTTPException(status_code=403, detail="Not a participant")
    return await service.get_messages(conversation_id, skip, limit)


@router.post("/{conversation_id}/messages", response_model=MessageRead, status_code=201)
async def send_message(
    conversation_id: uuid.UUID,
    payload: MessageCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.is_participant(conversation_id, user.id):
        raise HTTPException(status_code=403, detail="Not a participant")
    return await service.send_message(
        conversation_id=conversation_id,
        sender_id=user.id,
        content=payload.content,
        message_type=payload.message_type,
        attachment_url=payload.attachment_url,
    )


@router.patch("/{conversation_id}/read", status_code=204)
async def mark_conversation_read(
    conversation_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.is_participant(conversation_id, user.id):
        raise HTTPException(status_code=403, detail="Not a participant")
    await service.mark_read(conversation_id, user.id)


@router.patch("/{conversation_id}/archive", status_code=200)
async def archive_conversation(
    conversation_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    service = _get_service(session)
    if not await service.is_participant(conversation_id, user.id):
        raise HTTPException(status_code=403, detail="Not a participant")
    result = await service.archive(conversation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "archived"}

"""
Conversations API Routes

Chat conversation and message handling.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models import User, Project, Conversation, Message
from app.schemas import (
    MessageCreate,
    MessageResponse,
    ConversationResponse,
    ConversationListResponse,
)

router = APIRouter()


@router.get("/projects/{project_id}/conversations", response_model=ConversationListResponse)
async def list_conversations(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all conversations for a project."""
    # Verify project ownership
    project_result = await db.execute(
        select(Project)
        .where(Project.id == project_id, Project.user_id == current_user.id)
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")
    
    result = await db.execute(
        select(Conversation)
        .where(Conversation.project_id == project_id)
        .options(selectinload(Conversation.messages))
        .order_by(Conversation.created_at.desc())
    )
    conversations = result.scalars().all()
    
    return ConversationListResponse(
        conversations=[
            ConversationResponse(
                id=c.id,
                project_id=c.project_id,
                created_at=c.created_at,
                messages=[MessageResponse.model_validate(m) for m in c.messages]
            )
            for c in conversations
        ]
    )


@router.post("/projects/{project_id}/messages", response_model=MessageResponse)
async def send_message(
    project_id: str,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message in a project's conversation.
    
    Optionally triggers an agent run if trigger_agent is True.
    """
    # Verify project ownership
    project_result = await db.execute(
        select(Project)
        .where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get or create conversation
    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.project_id == project_id)
        .order_by(Conversation.created_at.desc())
        .limit(1)
    )
    conversation = conv_result.scalar_one_or_none()
    
    if not conversation:
        conversation = Conversation(project_id=project_id)
        db.add(conversation)
        await db.flush()
    
    # Create user message
    message = Message(
        conversation_id=conversation.id,
        role="user",
        content=message_data.content,
    )
    db.add(message)
    await db.flush()
    
    # If trigger_agent is True, we would start an agent run here
    # This will be implemented when we build the agent system
    if message_data.trigger_agent:
        # TODO: Start discovery agent run
        message.metadata = {"trigger_agent": True, "status": "pending"}
    
    return MessageResponse.model_validate(message)


@router.get("/projects/{project_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all messages for a project's conversation."""
    # Verify project ownership
    project_result = await db.execute(
        select(Project)
        .where(Project.id == project_id, Project.user_id == current_user.id)
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get conversation
    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.project_id == project_id)
        .options(selectinload(Conversation.messages))
        .order_by(Conversation.created_at.desc())
        .limit(1)
    )
    conversation = conv_result.scalar_one_or_none()
    
    if not conversation:
        return []
    
    return [MessageResponse.model_validate(m) for m in conversation.messages]

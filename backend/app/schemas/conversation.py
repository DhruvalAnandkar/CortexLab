"""
Conversation Schemas

Pydantic models for conversation and message requests/responses.
"""

from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class MessageCreate(BaseModel):
    """Request body for creating a message."""
    content: str
    trigger_agent: bool = False  # If true, triggers an agent run after the message


class MessageResponse(BaseModel):
    """Message data response."""
    id: str
    role: str
    content: str
    message_metadata: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation data response."""
    id: str
    project_id: str
    created_at: datetime
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """List of conversations response."""
    conversations: List[ConversationResponse]

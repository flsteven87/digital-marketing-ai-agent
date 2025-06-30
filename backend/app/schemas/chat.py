"""Pydantic schemas for chat-related API operations."""

from datetime import datetime
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class ChatSessionBase(BaseModel):
    """Base chat session schema."""
    title: Optional[str] = None
    context: Dict[str, Any] = {}
    is_archived: bool = False


class ChatSessionCreate(ChatSessionBase):
    """Schema for creating a new chat session."""
    user_id: UUID
    brand_id: Optional[UUID] = None


class ChatSessionUpdate(BaseModel):
    """Schema for updating a chat session."""
    title: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    is_archived: Optional[bool] = None


class ChatSession(ChatSessionBase):
    """Schema for chat session response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    brand_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class ChatMessageBase(BaseModel):
    """Base chat message schema."""
    role: Literal["user", "assistant", "system"]
    content: str
    metadata: Dict[str, Any] = {}


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a new chat message."""
    session_id: UUID


class ChatMessage(ChatMessageBase):
    """Schema for chat message response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    session_id: UUID
    created_at: datetime


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str
    session_id: Optional[UUID] = None
    user_id: str = "demo_user"  # Default for demo


class ChatResponse(BaseModel):
    """Schema for chat response."""
    message: str
    session_id: UUID
    message_id: UUID
    created_at: datetime


# Legacy compatibility
ChatSessionModel = ChatSession
ChatMessageModel = ChatMessage
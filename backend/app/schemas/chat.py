from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class ChatMessage(BaseModel):
    id: Optional[str] = None
    session_id: str
    user_id: str
    content: str
    role: str  # "user" or "assistant"
    created_at: Optional[datetime] = None


class ChatSession(BaseModel):
    id: str
    user_id: str
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    message: str
    session_id: str
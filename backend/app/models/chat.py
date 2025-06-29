from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from uuid import UUID


class ChatSessionModel(BaseModel):
    id: UUID
    user_id: UUID
    brand_id: Optional[UUID] = None
    title: Optional[str] = None
    context: Dict[str, Any] = {}
    is_archived: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatMessageModel(BaseModel):
    id: UUID
    session_id: UUID
    role: str  # 'user', 'assistant', 'system'
    content: str
    metadata: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True
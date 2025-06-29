from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from app.core.database import get_supabase
from app.models.chat import ChatSessionModel, ChatMessageModel


class ChatDatabaseService:
    def __init__(self):
        self.supabase = get_supabase()
    
    async def create_session(
        self, 
        user_id: UUID, 
        brand_id: Optional[UUID] = None,
        title: Optional[str] = None
    ) -> ChatSessionModel:
        """Create a new chat session"""
        session_data = {
            "id": str(uuid4()),
            "user_id": str(user_id),
            "brand_id": str(brand_id) if brand_id else None,
            "title": title,
            "context": {},
            "is_archived": False
        }
        
        result = self.supabase.table("chat_sessions").insert(session_data).execute()
        
        if result.data:
            return ChatSessionModel(**result.data[0])
        raise Exception("Failed to create chat session")
    
    async def get_user_sessions(
        self, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 10
    ) -> List[ChatSessionModel]:
        """Get chat sessions for a user"""
        result = self.supabase.table("chat_sessions")\
            .select("*")\
            .eq("user_id", str(user_id))\
            .eq("is_archived", False)\
            .order("updated_at", desc=True)\
            .range(skip, skip + limit - 1)\
            .execute()
        
        return [ChatSessionModel(**session) for session in result.data]
    
    async def get_session(self, session_id: UUID, user_id: UUID) -> Optional[ChatSessionModel]:
        """Get a specific chat session"""
        result = self.supabase.table("chat_sessions")\
            .select("*")\
            .eq("id", str(session_id))\
            .eq("user_id", str(user_id))\
            .single()\
            .execute()
        
        if result.data:
            return ChatSessionModel(**result.data)
        return None
    
    async def add_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> ChatMessageModel:
        """Add a message to a chat session"""
        message_data = {
            "id": str(uuid4()),
            "session_id": str(session_id),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        
        result = self.supabase.table("chat_messages").insert(message_data).execute()
        
        if result.data:
            # Update session's updated_at timestamp
            self.supabase.table("chat_sessions")\
                .update({"updated_at": datetime.utcnow().isoformat()})\
                .eq("id", str(session_id))\
                .execute()
            
            return ChatMessageModel(**result.data[0])
        raise Exception("Failed to add message")
    
    async def get_session_messages(
        self, 
        session_id: UUID, 
        user_id: UUID,
        skip: int = 0, 
        limit: int = 50
    ) -> List[ChatMessageModel]:
        """Get messages for a chat session"""
        # First verify user owns the session
        session = await self.get_session(session_id, user_id)
        if not session:
            raise Exception("Session not found or access denied")
        
        result = self.supabase.table("chat_messages")\
            .select("*")\
            .eq("session_id", str(session_id))\
            .order("created_at", desc=False)\
            .range(skip, skip + limit - 1)\
            .execute()
        
        return [ChatMessageModel(**message) for message in result.data]
    
    async def update_session_title(
        self, 
        session_id: UUID, 
        user_id: UUID, 
        title: str
    ) -> bool:
        """Update session title"""
        result = self.supabase.table("chat_sessions")\
            .update({"title": title})\
            .eq("id", str(session_id))\
            .eq("user_id", str(user_id))\
            .execute()
        
        return len(result.data) > 0
    
    async def archive_session(self, session_id: UUID, user_id: UUID) -> bool:
        """Archive a chat session"""
        result = self.supabase.table("chat_sessions")\
            .update({"is_archived": True})\
            .eq("id", str(session_id))\
            .eq("user_id", str(user_id))\
            .execute()
        
        return len(result.data) > 0
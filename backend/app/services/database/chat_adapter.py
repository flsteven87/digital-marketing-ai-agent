"""
Compatibility adapter for chat database operations.
This adapter maintains backward compatibility while using modern async SQLAlchemy repository.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from app.core.database_async import get_async_db
from app.services.database.chat_repository_async import ModernChatRepository
from app.models.chat_async import ChatSession, ChatMessage


class ChatDatabaseAdapter:
    """
    Adapter that provides backward compatibility for chat database operations.
    Uses modern async SQLAlchemy repository under the hood.
    
    This maintains API compatibility while using the new async infrastructure.
    """
    
    def __init__(self):
        # This will be initialized per request using dependency injection
        self._repository = None
    
    async def _get_repository(self) -> ModernChatRepository:
        """Get repository instance with database session"""
        if self._repository is None:
            # Create a new session for this request
            async for session in get_async_db():
                self._repository = ModernChatRepository(session)
                return self._repository
        return self._repository
    
    
    async def create_session(
        self, 
        user_id: UUID, 
        brand_id: Optional[UUID] = None,
        title: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session - maintains legacy interface"""
        repo = await self._get_repository()
        
        session = await repo.create_session(
            user_id=user_id,
            title=title,
            brand_id=brand_id
        )
        
        return session
    
    async def get_user_sessions(
        self, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 10
    ) -> List[ChatSession]:
        """Get chat sessions for a user"""
        repo = await self._get_repository()
        
        sessions = await repo.get_user_sessions(user_id, skip, limit)
        return sessions
    
    async def get_session(self, session_id: UUID, user_id: UUID) -> Optional[ChatSession]:
        """Get a specific chat session"""
        repo = await self._get_repository()
        
        session = await repo.get_session(session_id, user_id)
        return session
    
    async def add_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> ChatMessage:
        """Add a message to a chat session"""
        repo = await self._get_repository()
        
        message = await repo.add_message(
            session_id=session_id,
            role=role,
            content=content,
            metadata=metadata
        )
        
        return message
    
    async def get_session_messages(
        self, 
        session_id: UUID, 
        user_id: UUID,
        skip: int = 0, 
        limit: int = 50
    ) -> List[ChatMessage]:
        """Get messages for a chat session"""
        repo = await self._get_repository()
        
        messages = await repo.get_session_messages(session_id, user_id, skip, limit)
        return messages
    
    async def update_session_title(
        self, 
        session_id: UUID, 
        user_id: UUID, 
        title: str
    ) -> bool:
        """Update session title - maintains legacy interface"""
        repo = await self._get_repository()
        return await repo.update_session_title(session_id, user_id, title)
    
    async def archive_session(self, session_id: UUID, user_id: UUID) -> bool:
        """Archive a session - maintains legacy interface"""
        repo = await self._get_repository()
        return await repo.archive_session(session_id, user_id)
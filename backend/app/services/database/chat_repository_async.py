"""
Modern async chat repository using SQLAlchemy 2.0.
This will replace the legacy chat_repository.py
"""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.core.repository import AsyncRepository, AsyncChatRepository
from app.models.chat_async import ChatSession, ChatMessage
from app.schemas.chat import (
    ChatSessionCreate, ChatSessionUpdate,
    ChatMessageCreate
)


class ModernChatRepository:
    """
    Modern async chat repository with clean separation of concerns.
    Uses the generic repository pattern with chat-specific extensions.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.session_repo = AsyncChatRepository(ChatSession, session)
        self.message_repo = AsyncRepository(ChatMessage, session)
    
    # Chat Session Operations
    async def create_session(
        self, 
        user_id: UUID, 
        title: Optional[str] = None,
        brand_id: Optional[UUID] = None
    ) -> ChatSession:
        """Create a new chat session"""
        session_data = ChatSessionCreate(
            user_id=user_id,
            brand_id=brand_id,
            title=title or f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        return await self.session_repo.create(session_data)
    
    async def get_session(self, session_id: UUID, user_id: UUID) -> Optional[ChatSession]:
        """Get a chat session by ID and user ID"""
        stmt = (
            select(ChatSession)
            .where(ChatSession.id == session_id)
            .where(ChatSession.user_id == user_id)
            .where(ChatSession.is_archived == False)  # noqa
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_sessions(
        self, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 10
    ) -> List[ChatSession]:
        """Get all sessions for a user"""
        return await self.session_repo.get_user_sessions(user_id, skip, limit)
    
    async def update_session_title(
        self, 
        session_id: UUID, 
        user_id: UUID, 
        title: str
    ) -> bool:
        """Update session title"""
        session = await self.get_session(session_id, user_id)
        if not session:
            return False
        
        update_data = ChatSessionUpdate(title=title)
        updated_session = await self.session_repo.update(session_id, update_data)
        return updated_session is not None
    
    async def archive_session(self, session_id: UUID, user_id: UUID) -> bool:
        """Archive a session (soft delete)"""
        session = await self.get_session(session_id, user_id)
        if not session:
            return False
        
        update_data = ChatSessionUpdate(is_archived=True)
        updated_session = await self.session_repo.update(session_id, update_data)
        return updated_session is not None
    
    # Chat Message Operations
    async def add_message(
        self, 
        session_id: UUID, 
        role: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """Add a message to a chat session"""
        message_data = ChatMessageCreate(
            session_id=session_id,
            role=role,
            content=content,
            message_metadata=metadata or {}
        )
        
        # Create the message
        message = await self.message_repo.create(message_data)
        
        # Update session timestamp
        await self._update_session_timestamp(session_id)
        
        return message
    
    async def get_session_messages(
        self, 
        session_id: UUID, 
        user_id: UUID,
        skip: int = 0, 
        limit: int = 50
    ) -> List[ChatMessage]:
        """Get messages for a chat session"""
        # First verify the user owns the session
        session = await self.get_session(session_id, user_id)
        if not session:
            return []
        
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_session_with_messages(
        self, 
        session_id: UUID, 
        user_id: UUID
    ) -> Optional[ChatSession]:
        """Get session with all messages loaded"""
        return await self.session_repo.get_session_with_messages(session_id, user_id)
    
    # Helper Methods
    async def _update_session_timestamp(self, session_id: UUID) -> None:
        """Update session's updated_at timestamp"""
        stmt = (
            select(ChatSession)
            .where(ChatSession.id == session_id)
        )
        result = await self.session.execute(stmt)
        session = result.scalar_one_or_none()
        
        if session:
            session.updated_at = datetime.utcnow()
            await self.session.flush()
    
    # Statistics and Analytics
    async def get_session_message_count(self, session_id: UUID) -> int:
        """Get the number of messages in a session"""
        stmt = (
            select(func.count(ChatMessage.id))
            .where(ChatMessage.session_id == session_id)
        )
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def get_user_session_count(self, user_id: UUID) -> int:
        """Get the number of sessions for a user"""
        stmt = (
            select(func.count(ChatSession.id))
            .where(ChatSession.user_id == user_id)
            .where(ChatSession.is_archived == False)  # noqa
        )
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0


# Dependency for FastAPI route injection
async def get_chat_repository(session: AsyncSession) -> ModernChatRepository:
    """Factory function for dependency injection"""
    return ModernChatRepository(session)
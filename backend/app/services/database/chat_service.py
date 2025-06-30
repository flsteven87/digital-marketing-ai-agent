"""Chat service using the new repository pattern.

This service provides high-level chat operations using the repository pattern,
replacing the old adapter-based approach.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.core.database_async import get_async_db
from app.repositories.chat import ChatSessionRepository, ChatMessageRepository
from app.models.chat_async import ChatSession, ChatMessage


class ChatDatabaseService:
    """Service for chat database operations using repository pattern."""
    
    def __init__(self):
        self._session = None
        self._session_repo = None
        self._message_repo = None
        self._initialized = False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_repos()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()
            self._session = None
            self._session_repo = None
            self._message_repo = None
            self._initialized = False
    
    async def _ensure_repos(self):
        """Ensure repositories are initialized with a session."""
        if not self._initialized:
            async for session in get_async_db():
                self._session = session
                self._session_repo = ChatSessionRepository(ChatSession, session)
                self._message_repo = ChatMessageRepository(ChatMessage, session)
                self._initialized = True
                break
    
    async def create_session(
        self,
        user_id: UUID,
        title: Optional[str] = None,
        brand_id: Optional[UUID] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """Create a new chat session.
        
        Args:
            user_id: User's UUID
            title: Session title
            brand_id: Optional brand UUID
            context: Optional session context
            
        Returns:
            Created chat session
        """
        await self._ensure_repos()
        
        title = title or f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return await self._session_repo.create(
            user_id=user_id,
            title=title,
            brand_id=brand_id,
            session_context=context or {}
        )
    
    async def get_session(
        self,
        session_id: UUID,
        user_id: Optional[UUID] = None
    ) -> Optional[ChatSession]:
        """Get a chat session.
        
        Args:
            session_id: Session UUID
            user_id: Optional user UUID for verification
            
        Returns:
            Chat session or None
        """
        await self._ensure_repos()
        
        if user_id:
            return await self._session_repo.get_by(
                id=session_id,
                user_id=user_id
            )
        else:
            return await self._session_repo.get(session_id)
    
    async def get_user_sessions(
        self,
        user_id: UUID,
        include_archived: bool = False,
        skip: int = 0,
        limit: int = 20
    ) -> List[ChatSession]:
        """Get all sessions for a user.
        
        Args:
            user_id: User's UUID
            include_archived: Whether to include archived sessions
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of chat sessions
        """
        await self._ensure_repos()
        
        return await self._session_repo.get_user_sessions(
            user_id=user_id,
            include_archived=include_archived,
            skip=skip,
            limit=limit
        )
    
    async def add_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """Add a message to a session.
        
        Args:
            session_id: Session UUID
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            Created message
        """
        await self._ensure_repos()
        
        # Update session's updated_at timestamp
        await self._session_repo.update(
            session_id,
            updated_at=datetime.utcnow()
        )
        
        return await self._message_repo.add_message(
            session_id=session_id,
            role=role,
            content=content,
            metadata=metadata
        )
    
    async def get_session_messages(
        self,
        session_id: UUID,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ChatMessage]:
        """Get messages for a session.
        
        Args:
            session_id: Session UUID
            user_id: Optional user UUID for verification
            skip: Number of messages to skip
            limit: Maximum number of messages
            
        Returns:
            List of messages
        """
        await self._ensure_repos()
        
        # Verify session ownership if user_id provided
        if user_id:
            session = await self._session_repo.get_by(
                id=session_id,
                user_id=user_id
            )
            if not session:
                return []
        
        return await self._message_repo.get_session_messages(
            session_id=session_id,
            skip=skip,
            limit=limit
        )
    
    async def update_session_title(
        self,
        session_id: UUID,
        user_id: UUID,
        title: str
    ) -> bool:
        """Update session title.
        
        Args:
            session_id: Session UUID
            user_id: User UUID for verification
            title: New title
            
        Returns:
            True if updated, False otherwise
        """
        await self._ensure_repos()
        
        # Verify ownership
        session = await self._session_repo.get_by(
            id=session_id,
            user_id=user_id
        )
        
        if not session:
            return False
        
        updated = await self._session_repo.update_session_title(
            session_id=session_id,
            title=title
        )
        
        return updated is not None
    
    async def archive_session(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> bool:
        """Archive a session.
        
        Args:
            session_id: Session UUID
            user_id: User UUID for verification
            
        Returns:
            True if archived, False otherwise
        """
        await self._ensure_repos()
        
        # Verify ownership
        session = await self._session_repo.get_by(
            id=session_id,
            user_id=user_id
        )
        
        if not session:
            return False
        
        updated = await self._session_repo.archive_session(session_id)
        return updated is not None
    
    async def search_sessions(
        self,
        user_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[ChatSession]:
        """Search user's sessions.
        
        Args:
            user_id: User's UUID
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of matching sessions
        """
        await self._ensure_repos()
        
        return await self._session_repo.search_sessions(
            user_id=user_id,
            query=query,
            skip=skip,
            limit=limit
        )
    
    async def get_session_statistics(
        self,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Get chat statistics.
        
        Args:
            user_id: Optional user UUID to filter by
            
        Returns:
            Dictionary with statistics
        """
        await self._ensure_repos()
        
        session_stats = await self._session_repo.get_session_statistics(user_id)
        
        # Get message statistics for the last 30 days
        message_stats = await self._message_repo.get_message_statistics()
        
        return {
            **session_stats,
            **message_stats
        }
    
    async def get_recent_conversations(
        self,
        user_id: UUID,
        days: int = 7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent conversations with preview.
        
        Args:
            user_id: User's UUID
            days: Number of days to look back
            limit: Maximum number of conversations
            
        Returns:
            List of conversations with last message preview
        """
        await self._ensure_repos()
        
        sessions = await self._session_repo.get_recent_sessions(
            user_id=user_id,
            days=days,
            limit=limit
        )
        
        conversations = []
        for session in sessions:
            # Get last message for preview
            last_messages = await self._message_repo.get_last_messages(
                session_id=session.id,
                count=1
            )
            
            conversation = {
                'session_id': str(session.id),
                'title': session.title,
                'updated_at': session.updated_at.isoformat(),
                'message_count': await self._message_repo.count_session_messages(session.id),
                'last_message': {
                    'role': last_messages[0].role,
                    'content': last_messages[0].content[:100] + '...' if len(last_messages[0].content) > 100 else last_messages[0].content,
                    'created_at': last_messages[0].created_at.isoformat()
                } if last_messages else None
            }
            conversations.append(conversation)
        
        return conversations
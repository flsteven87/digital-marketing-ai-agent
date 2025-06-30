"""Chat repository for managing chat sessions and messages."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.chat_async import ChatSession, ChatMessage


class ChatSessionRepository(BaseRepository[ChatSession]):
    """Repository for chat session operations."""
    
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
            limit: Maximum number of records to return
            
        Returns:
            List of chat sessions
        """
        filters = {'user_id': user_id}
        if not include_archived:
            filters['is_archived'] = False
        
        return await self.get_all(
            skip=skip,
            limit=limit,
            order_by='-updated_at',
            **filters
        )
    
    async def get_session_with_messages(
        self, 
        session_id: UUID,
        message_limit: int = 50
    ) -> Optional[ChatSession]:
        """Get a session with its messages loaded.
        
        Args:
            session_id: Session UUID
            message_limit: Maximum number of messages to load
            
        Returns:
            ChatSession with messages or None
        """
        stmt = (
            select(ChatSession)
            .where(ChatSession.id == session_id)
            .options(
                selectinload(ChatSession.messages).limit(message_limit)
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def archive_session(self, session_id: UUID) -> Optional[ChatSession]:
        """Archive a chat session.
        
        Args:
            session_id: Session UUID
            
        Returns:
            Updated session or None
        """
        return await self.update(session_id, is_archived=True)
    
    async def unarchive_session(self, session_id: UUID) -> Optional[ChatSession]:
        """Unarchive a chat session.
        
        Args:
            session_id: Session UUID
            
        Returns:
            Updated session or None
        """
        return await self.update(session_id, is_archived=False)
    
    async def update_session_title(
        self, 
        session_id: UUID, 
        title: str
    ) -> Optional[ChatSession]:
        """Update session title.
        
        Args:
            session_id: Session UUID
            title: New title
            
        Returns:
            Updated session or None
        """
        return await self.update(session_id, title=title)
    
    async def get_recent_sessions(
        self,
        user_id: UUID,
        days: int = 7,
        limit: int = 10
    ) -> List[ChatSession]:
        """Get user's recent sessions.
        
        Args:
            user_id: User's UUID
            days: Number of days to look back
            limit: Maximum number of sessions
            
        Returns:
            List of recent sessions
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        stmt = (
            select(ChatSession)
            .where(
                ChatSession.user_id == user_id,
                ChatSession.is_archived == False,
                ChatSession.updated_at >= cutoff_date
            )
            .order_by(ChatSession.updated_at.desc())
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def search_sessions(
        self,
        user_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[ChatSession]:
        """Search user's sessions by title or content.
        
        Args:
            user_id: User's UUID
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching sessions
        """
        search_pattern = f"%{query}%"
        
        # Search in session titles and message content
        stmt = (
            select(ChatSession)
            .distinct()
            .join(ChatSession.messages)
            .where(
                ChatSession.user_id == user_id,
                ChatSession.is_archived == False,
                and_(
                    ChatSession.title.ilike(search_pattern)
                    | ChatMessage.content.ilike(search_pattern)
                )
            )
            .order_by(ChatSession.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_session_statistics(
        self, 
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Get chat session statistics.
        
        Args:
            user_id: Optional user UUID to filter by
            
        Returns:
            Dictionary with session statistics
        """
        base_query = select(func.count()).select_from(ChatSession)
        
        if user_id:
            base_query = base_query.where(ChatSession.user_id == user_id)
        
        # Total sessions
        total_result = await self.session.execute(base_query)
        total_sessions = total_result.scalar() or 0
        
        # Active sessions
        active_query = base_query.where(ChatSession.is_archived == False)
        active_result = await self.session.execute(active_query)
        active_sessions = active_result.scalar() or 0
        
        # Sessions in last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_query = base_query.where(ChatSession.created_at >= seven_days_ago)
        recent_result = await self.session.execute(recent_query)
        recent_sessions = recent_result.scalar() or 0
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'archived_sessions': total_sessions - active_sessions,
            'sessions_last_7_days': recent_sessions
        }


class ChatMessageRepository(BaseRepository[ChatMessage]):
    """Repository for chat message operations."""
    
    async def get_session_messages(
        self,
        session_id: UUID,
        skip: int = 0,
        limit: int = 50,
        reverse: bool = False
    ) -> List[ChatMessage]:
        """Get messages for a session.
        
        Args:
            session_id: Session UUID
            skip: Number of messages to skip
            limit: Maximum number of messages
            reverse: If True, get newest messages first
            
        Returns:
            List of messages
        """
        order = '-created_at' if reverse else 'created_at'
        
        return await self.get_all(
            skip=skip,
            limit=limit,
            order_by=order,
            session_id=session_id
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
        return await self.create(
            session_id=session_id,
            role=role,
            content=content,
            metadata=metadata or {}
        )
    
    async def get_last_messages(
        self,
        session_id: UUID,
        count: int = 5,
        role: Optional[str] = None
    ) -> List[ChatMessage]:
        """Get the last N messages from a session.
        
        Args:
            session_id: Session UUID
            count: Number of messages to retrieve
            role: Optional role filter
            
        Returns:
            List of messages (newest first)
        """
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
        )
        
        if role:
            stmt = stmt.where(ChatMessage.role == role)
        
        stmt = stmt.order_by(ChatMessage.created_at.desc()).limit(count)
        
        result = await self.session.execute(stmt)
        messages = list(result.scalars().all())
        
        # Reverse to get chronological order
        return list(reversed(messages))
    
    async def count_session_messages(
        self,
        session_id: UUID,
        role: Optional[str] = None
    ) -> int:
        """Count messages in a session.
        
        Args:
            session_id: Session UUID
            role: Optional role filter
            
        Returns:
            Number of messages
        """
        filters = {'session_id': session_id}
        if role:
            filters['role'] = role
        
        return await self.count(**filters)
    
    async def search_messages(
        self,
        query: str,
        session_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ChatMessage]:
        """Search messages by content.
        
        Args:
            query: Search query
            session_id: Optional session filter
            user_id: Optional user filter (requires join)
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of matching messages
        """
        search_pattern = f"%{query}%"
        
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.content.ilike(search_pattern))
        )
        
        if session_id:
            stmt = stmt.where(ChatMessage.session_id == session_id)
        
        if user_id:
            stmt = stmt.join(ChatSession).where(ChatSession.user_id == user_id)
        
        stmt = stmt.order_by(ChatMessage.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_message_statistics(
        self,
        session_id: Optional[UUID] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get message statistics.
        
        Args:
            session_id: Optional session filter
            days: Number of days to analyze
            
        Returns:
            Dictionary with message statistics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        base_query = select(func.count()).select_from(ChatMessage)
        
        if session_id:
            base_query = base_query.where(ChatMessage.session_id == session_id)
        
        base_query = base_query.where(ChatMessage.created_at >= cutoff_date)
        
        # Total messages
        total_result = await self.session.execute(base_query)
        total_messages = total_result.scalar() or 0
        
        # Messages by role
        user_query = base_query.where(ChatMessage.role == 'user')
        user_result = await self.session.execute(user_query)
        user_messages = user_result.scalar() or 0
        
        assistant_query = base_query.where(ChatMessage.role == 'assistant')
        assistant_result = await self.session.execute(assistant_query)
        assistant_messages = assistant_result.scalar() or 0
        
        return {
            'total_messages': total_messages,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'average_per_day': total_messages / days if days > 0 else 0
        }
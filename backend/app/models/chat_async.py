"""
Modern async SQLAlchemy models for chat functionality.
Uses the new async Base and modern patterns.
"""
from datetime import datetime
from typing import Optional, List
from uuid import uuid4, UUID
from sqlalchemy import String, Boolean, DateTime, Text, JSON, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database_async import Base


class ChatSession(Base):
    """Modern chat session model with type annotations."""
    __tablename__ = "chat_sessions"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Foreign keys - temporarily without FK constraint until user model migration
    user_id: Mapped[UUID] = mapped_column(
        nullable=False, 
        index=True
    )
    # Brand ID - temporarily without FK constraint until brands model is implemented
    brand_id: Mapped[Optional[UUID]] = mapped_column(
        index=True
    )
    
    # Session data
    title: Mapped[Optional[str]] = mapped_column(String(255))
    session_context: Mapped[dict] = mapped_column("context", JSON, default=dict)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    # Relationships (will be defined when user models are migrated)
    # user: Mapped["User"] = relationship("User", back_populates="chat_sessions")
    # brand: Mapped[Optional["Brand"]] = relationship("Brand", back_populates="chat_sessions")
    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage", 
        back_populates="session", 
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )
    # generated_content: Mapped[List["GeneratedContent"]] = relationship(
    #     "GeneratedContent", back_populates="session"
    # )

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, title='{self.title}')>"


class ChatMessage(Base):
    """Modern chat message model with type annotations."""
    __tablename__ = "chat_messages"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Foreign key
    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("chat_sessions.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Message data
    role: Mapped[str] = mapped_column(
        String(20), 
        CheckConstraint("role IN ('user', 'assistant', 'system')"),
        nullable=False,
        index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        index=True
    )

    # Relationships
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, role='{self.role}')>"

    @property
    def is_user_message(self) -> bool:
        """Check if this is a user message"""
        return self.role == "user"

    @property
    def is_assistant_message(self) -> bool:
        """Check if this is an assistant message"""
        return self.role == "assistant"
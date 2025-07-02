"""
Modern async SQLAlchemy models for the AI Marketing Assistant.
Import all async models here to ensure they are registered with SQLAlchemy.
"""

from app.core.database_async import Base

# Import all async models to register them with SQLAlchemy
from app.models.user_async import (
    User, 
    OAuthProvider, 
    UserSession, 
    AuthAuditLog,
    Organization,
    Brand,
    GeneratedContent
)
from app.models.chat_async import ChatSession, ChatMessage

# Export all async models for easy importing
__all__ = [
    "Base",
    "User",
    "OAuthProvider", 
    "UserSession",
    "AuthAuditLog",
    "Organization",
    "Brand",
    "GeneratedContent",
    "ChatSession",
    "ChatMessage",
]
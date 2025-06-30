"""SQLAlchemy models for the AI Marketing Assistant.

Import all models here to ensure they are registered with SQLAlchemy.
"""

from app.core.database import Base

# Import all models to register them with SQLAlchemy
from app.models.user import User, OAuthProvider, UserSession, AuthAuditLog
from app.models.chat import ChatSession, ChatMessage
from app.models.content import Organization, Brand, GeneratedContent

# Export all models for easy importing
__all__ = [
    "Base",
    "User",
    "OAuthProvider", 
    "UserSession",
    "AuthAuditLog",
    "ChatSession",
    "ChatMessage",
    "Organization",
    "Brand",
    "GeneratedContent",
]
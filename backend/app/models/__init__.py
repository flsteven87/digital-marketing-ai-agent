"""SQLAlchemy models for the AI Marketing Assistant.

Import all models here to ensure they are registered with SQLAlchemy.
"""

from app.core.database import Base

# Import all models to register them with SQLAlchemy
from app.models.user import User, OAuthProvider, UserSession, AuthAuditLog
# Note: Chat models moved to chat_async.py for modern async architecture
from app.models.content import Organization, Brand, GeneratedContent

# Export all models for easy importing (excluding chat models)
__all__ = [
    "Base",
    "User",
    "OAuthProvider", 
    "UserSession",
    "AuthAuditLog",
    "Organization",
    "Brand",
    "GeneratedContent",
]
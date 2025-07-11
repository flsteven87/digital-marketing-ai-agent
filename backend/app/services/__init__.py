"""
Service layer for the AI Marketing Assistant.

This module provides a clean interface to all services used in the application.
"""

# AI Services
from .ai.chat_orchestrator import ChatService
from .ai.base_agent import BaseAgent

# Auth Services  
from .auth.google_oauth import GoogleOAuthService
from .auth.jwt_service import JWTService
from .auth.user_service import UserService

# Database Services (legacy services removed, using modern async adapters)

__all__ = [
    # AI
    "ChatService",
    "BaseAgent",
    # Auth
    "GoogleOAuthService",
    "JWTService",
    "UserService",
    # Database services now use modern async adapters
]
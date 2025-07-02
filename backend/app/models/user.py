"""DEPRECATED: Legacy SQLAlchemy models for user and authentication.

⚠️  DEPRECATED: This file is deprecated as of Phase 1 database architecture unification.
Use app.models.user_async.py for all new development.

This file is kept for backward compatibility during the transition period
and will be removed in a future version.
"""

from uuid import uuid4
from sqlalchemy import Column, String, Boolean, DateTime, UUID, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """User model for authentication and profile management."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, default=False)
    name = Column(String(255))
    avatar_url = Column(Text)
    locale = Column(String(10), default="en")
    company = Column(String(255))
    role = Column(String(50), default="user")
    phone = Column(String(20))
    timezone = Column(String(50), default="UTC")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, index=True)
    user_metadata = Column("metadata", JSON, default=dict)

    # Relationships
    oauth_providers = relationship("OAuthProvider", back_populates="user", cascade="all, delete-orphan")
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    # Note: chat_sessions relationship removed due to different base class (async models)
    organizations = relationship("Organization", back_populates="owner", cascade="all, delete-orphan")
    generated_content = relationship("GeneratedContent", back_populates="user", cascade="all, delete-orphan")


class OAuthProvider(Base):
    """OAuth provider information for users."""
    __tablename__ = "oauth_providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)  # 'google', 'github', etc.
    provider_user_id = Column(String(255), nullable=False)
    provider_email = Column(String(255))
    provider_data = Column(JSON, default=dict)  # Store additional provider data
    access_token = Column(Text)  # TODO: Encrypt in production
    refresh_token = Column(Text)  # TODO: Encrypt in production
    token_expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="oauth_providers")

    # Constraints
    __table_args__ = (
        # Unique constraint on provider and provider_user_id
        {"schema": "public"},
    )


class UserSession(Base):
    """User session management."""
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45))  # Supports both IPv4 and IPv6
    user_agent = Column(Text)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True, index=True)

    # Relationships
    user = relationship("User", back_populates="user_sessions")


class AuthAuditLog(Base):
    """Authentication audit log for security tracking."""
    __tablename__ = "auth_audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    action = Column(String(50), nullable=False, index=True)  # 'login', 'logout', 'token_refresh', etc.
    ip_address = Column(String(45))
    user_agent = Column(Text)
    provider = Column(String(50))  # OAuth provider used
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    audit_metadata = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Note: No direct relationship to User to allow for auditing deleted users
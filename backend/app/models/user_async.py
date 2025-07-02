"""
Modern async SQLAlchemy models for user and authentication.
Uses the new async Base and modern type annotations.
"""
from datetime import datetime
from typing import Optional, List
from uuid import uuid4, UUID
from sqlalchemy import String, Boolean, DateTime, Text, JSON, ForeignKey, CheckConstraint, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database_async import Base


class User(Base):
    """Modern async user model with type annotations."""
    __tablename__ = "users"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Core user fields
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    locale: Mapped[str] = mapped_column(String(10), default="en")
    company: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="user")
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    
    # Status and metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    user_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    oauth_providers: Mapped[List["OAuthProvider"]] = relationship(
        "OAuthProvider", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    user_sessions: Mapped[List["UserSession"]] = relationship(
        "UserSession", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    chat_sessions: Mapped[List["ChatSession"]] = relationship(
        "ChatSession", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    organizations: Mapped[List["Organization"]] = relationship(
        "Organization", 
        back_populates="owner", 
        cascade="all, delete-orphan"
    )
    generated_content: Mapped[List["GeneratedContent"]] = relationship(
        "GeneratedContent", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"


class OAuthProvider(Base):
    """Modern async OAuth provider model with type annotations."""
    __tablename__ = "oauth_providers"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Foreign key
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Provider information
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_email: Mapped[Optional[str]] = mapped_column(String(255))
    provider_data: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Token information (TODO: Encrypt in production)
    access_token: Mapped[Optional[str]] = mapped_column(Text)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="oauth_providers")

    def __repr__(self) -> str:
        return f"<OAuthProvider(id={self.id}, provider='{self.provider}')>"


class UserSession(Base):
    """Modern async user session model with type annotations."""
    __tablename__ = "user_sessions"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Foreign key
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Session information
    session_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # Supports both IPv4 and IPv6
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Timestamps
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_sessions")

    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"


class AuthAuditLog(Base):
    """Modern async authentication audit log model with type annotations."""
    __tablename__ = "auth_audit_log"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Foreign key (nullable to allow auditing deleted users)
    user_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), 
        index=True
    )
    
    # Audit information
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    provider: Mapped[Optional[str]] = mapped_column(String(50))
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    audit_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        index=True
    )

    def __repr__(self) -> str:
        return f"<AuthAuditLog(id={self.id}, action='{self.action}')>"


class Organization(Base):
    """Modern async organization model with type annotations."""
    __tablename__ = "organizations"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Foreign key
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Organization information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text)
    website: Mapped[Optional[str]] = mapped_column(Text)
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="organizations")
    brands: Mapped[List["Brand"]] = relationship(
        "Brand", 
        back_populates="organization", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}')>"


class Brand(Base):
    """Modern async brand model with type annotations."""
    __tablename__ = "brands"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Foreign key
    organization_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), 
        index=True
    )
    
    # Brand information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    logo_url: Mapped[Optional[str]] = mapped_column(Text)
    website: Mapped[Optional[str]] = mapped_column(Text)
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    target_audience: Mapped[Optional[str]] = mapped_column(Text)
    brand_voice: Mapped[Optional[str]] = mapped_column(Text)
    brand_values: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    color_palette: Mapped[dict] = mapped_column(JSON, default=dict)
    social_profiles: Mapped[dict] = mapped_column(JSON, default=dict)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="brands")
    chat_sessions: Mapped[List["ChatSession"]] = relationship(
        "ChatSession", 
        back_populates="brand"
    )
    generated_content: Mapped[List["GeneratedContent"]] = relationship(
        "GeneratedContent", 
        back_populates="brand"
    )

    def __repr__(self) -> str:
        return f"<Brand(id={self.id}, name='{self.name}')>"


class GeneratedContent(Base):
    """Modern async generated content model with type annotations."""
    __tablename__ = "generated_content"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    brand_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("brands.id", ondelete="SET NULL"), 
        index=True
    )
    session_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("chat_sessions.id", ondelete="SET NULL"), 
        index=True
    )
    
    # Content information
    content_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    platform: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    media_urls: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    hashtags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    content_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    
    # Scheduling
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="generated_content")
    brand: Mapped[Optional["Brand"]] = relationship("Brand", back_populates="generated_content")
    session: Mapped[Optional["ChatSession"]] = relationship("ChatSession", back_populates="generated_content")

    def __repr__(self) -> str:
        return f"<GeneratedContent(id={self.id}, content_type='{self.content_type}')>"
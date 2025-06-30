"""SQLAlchemy models for content and marketing functionality."""

from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy import Column, String, Boolean, DateTime, UUID, Text, JSON, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Organization(Base):
    """Organization model for multi-tenant support."""
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    logo_url = Column(Text)
    website = Column(Text)
    industry = Column(String(100))
    description = Column(Text)
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="organizations")
    brands = relationship("Brand", back_populates="organization", cascade="all, delete-orphan")


class Brand(Base):
    """Brand model for marketing campaigns."""
    __tablename__ = "brands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    logo_url = Column(Text)
    website = Column(Text)
    industry = Column(String(100))
    target_audience = Column(Text)
    brand_voice = Column(Text)
    brand_values = Column(ARRAY(String))
    color_palette = Column(JSON, default=dict)
    social_profiles = Column(JSON, default=dict)
    settings = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="brands")
    # Note: chat_sessions relationship removed (moved to async models)
    generated_content = relationship("GeneratedContent", back_populates="brand")


class GeneratedContent(Base):
    """Generated content model for marketing materials."""
    __tablename__ = "generated_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id", ondelete="SET NULL"), index=True)
    # Temporarily removed FK constraint to chat_sessions (moved to async models)
    session_id = Column(UUID(as_uuid=True), index=True)
    content_type = Column(String(50), nullable=False, index=True)
    platform = Column(ARRAY(String))
    title = Column(String(255))
    content = Column(Text, nullable=False)
    media_urls = Column(ARRAY(String))
    hashtags = Column(ARRAY(String))
    content_metadata = Column("metadata", JSON, default=dict)
    status = Column(String(20), default="draft", index=True)
    scheduled_at = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="generated_content")
    brand = relationship("Brand", back_populates="generated_content")
    # Note: session relationship removed (chat_sessions moved to async models)
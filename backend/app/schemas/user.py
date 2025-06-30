"""Pydantic schemas for user-related API operations."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None
    role: str = "user"
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    timezone: str = "UTC"
    locale: str = "en"
    is_active: bool = True
    metadata: Dict[str, Any] = {}


class UserCreate(UserBase):
    """Schema for creating a new user."""
    email_verified: bool = False


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    name: Optional[str] = None
    company: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class User(UserBase):
    """Schema for user response with all fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None


class UserProfile(BaseModel):
    """Simplified user profile for public display."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: Optional[str]
    avatar_url: Optional[str]
    role: str


# Legacy compatibility
UserModel = User  # For backward compatibility
"""Authentication related Pydantic schemas."""

from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    email: str
    password: str


class UserRegister(BaseModel):
    email: str
    password: str
    name: str
    company: Optional[str] = None


class GoogleOAuthRequest(BaseModel):
    """Request schema for Google OAuth callback."""
    code: str
    state: Optional[str] = None


class TokenResponse(BaseModel):
    """Response schema for token operations."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None


class UserProfile(BaseModel):
    """User profile schema."""
    id: UUID
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    company: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class LoginResponse(BaseModel):
    """Login response schema."""
    user: UserProfile
    tokens: TokenResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class UpdateProfileRequest(BaseModel):
    """Update profile request schema."""
    name: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None


class AuthorizationUrlResponse(BaseModel):
    """Authorization URL response schema."""
    authorization_url: str
    state: str


class OAuthProviderInfo(BaseModel):
    """OAuth provider information."""
    provider: str
    client_id: str
    authorization_url: str
    scopes: list[str]
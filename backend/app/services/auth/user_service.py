"""User management service with OAuth integration using unified repository pattern."""

from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.core.database_async import get_async_db
from app.repositories.user import UserRepository
from app.repositories.oauth import OAuthProviderRepository
from app.models.user import User as UserModel, OAuthProvider
from app.services.auth.jwt_service import JWTService
from app.core.exceptions import AuthenticationError, UserNotFoundError


class UserService:
    """User management with OAuth and JWT integration using unified repository pattern."""
    
    def __init__(self):
        self.jwt_service = JWTService()
        self._session = None
        self._user_repo = None
        self._oauth_repo = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        async for session in get_async_db():
            self._session = session
            self._user_repo = UserRepository(UserModel, session)
            self._oauth_repo = OAuthProviderRepository(OAuthProvider, session)
            break
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Note: Session is managed by get_async_db dependency, don't close manually
        self._session = None
        self._user_repo = None
        self._oauth_repo = None
    
    def _serialize_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert database types to API-ready format."""
        return {
            **user_data,
            "id": str(user_data["id"]),
            "created_at": user_data["created_at"].isoformat(),
            "updated_at": user_data["updated_at"].isoformat(),
        }
    
    def _convert_user_to_dict(self, user: UserModel) -> Dict[str, Any]:
        """Convert SQLAlchemy User model to dictionary."""
        return {
            "id": user.id,
            "email": user.email,
            "email_verified": user.email_verified,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "locale": user.locale,
            "company": user.company,
            "role": user.role,
            "phone": user.phone,
            "timezone": user.timezone,
            "is_active": user.is_active,
            "metadata": user.user_metadata or {},
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login_at": user.last_login_at
        }
    
    async def create_or_update_user_from_google(self, google_user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update user from Google OAuth data.
        
        Args:
            google_user_data: User data from Google OAuth
            
        Returns:
            User data with tokens
        """
        email = google_user_data["email"]
        google_id = google_user_data["id"]
        
        # Check if user exists
        existing_user = await self.get_user_by_email(email)
        
        if existing_user:
            # Update existing user with Google data
            user_data = await self.update_user_google_info(existing_user["id"], google_user_data)
        else:
            # Create new user
            user_data = await self.create_user_from_google(google_user_data)
        
        # Store/update OAuth provider info
        await self.store_oauth_provider_info(user_data["id"], "google", google_user_data)
        
        # Generate tokens
        tokens = self.jwt_service.create_token_pair(
            user_id=str(user_data["id"]),
            additional_claims={
                "email": user_data["email"],
                "name": user_data["name"]
            }
        )
        
        return {
            "user": user_data,
            "tokens": tokens
        }
    
    async def create_user_from_google(self, google_user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user from Google OAuth data."""
        if not self._user_repo:
            raise RuntimeError("UserService must be used as async context manager")
        
        # Create user using repository
        user = await self._user_repo.create(
            email=google_user_data["email"],
            email_verified=google_user_data.get("email_verified", False),
            name=google_user_data.get("name", ""),
            avatar_url=google_user_data.get("picture", ""),
            locale=google_user_data.get("locale", "en"),
            role="user",
            is_active=True,
            user_metadata={
                "oauth_provider": "google",
                "google_id": google_user_data["id"]
            }
        )
        
        return self._convert_user_to_dict(user)
    
    async def update_user_google_info(self, user_id: str, google_user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing user with Google OAuth data."""
        if not self._user_repo:
            raise RuntimeError("UserService must be used as async context manager")
        
        # Update user using repository
        user = await self._user_repo.update(
            UUID(user_id),
            name=google_user_data.get("name", ""),
            avatar_url=google_user_data.get("picture", ""),
            email_verified=google_user_data.get("email_verified", False),
            last_login_at=datetime.utcnow()
        )
        
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        return self._convert_user_to_dict(user)
    
    async def store_oauth_provider_info(self, user_id: str, provider: str, provider_data: Dict[str, Any]) -> None:
        """Store or update OAuth provider information."""
        if not self._oauth_repo:
            raise RuntimeError("UserService must be used as async context manager")
        
        # Use repository to create or update OAuth provider
        await self._oauth_repo.create_or_update_provider(
            user_id=UUID(user_id),
            provider=provider,
            provider_user_id=provider_data["id"],
            provider_email=provider_data.get("email"),
            provider_data=provider_data
        )
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address."""
        if not self._user_repo:
            raise RuntimeError("UserService must be used as async context manager")
        
        user = await self._user_repo.get_by_email(email)
        if user:
            return self._convert_user_to_dict(user)
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        if not self._user_repo:
            raise RuntimeError("UserService must be used as async context manager")
        
        user = await self._user_repo.get(UUID(user_id))
        if user:
            return self._convert_user_to_dict(user)
        return None
"""User service v2 using repository pattern."""

from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import select

from app.core.database_async import get_async_db
from app.repositories.user import UserRepository
from app.models.user_async import User, OAuthProvider
from app.services.auth.jwt_service import JWTService
from app.core.exceptions import AuthenticationError, UserNotFoundError


class UserService:
    """User management service using repository pattern."""
    
    def __init__(self):
        self.jwt_service = JWTService()
        self._session = None
        self._user_repo = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()
    
    async def _ensure_repo(self):
        """Ensure repository is initialized with a session."""
        if not self._user_repo:
            async for session in get_async_db():
                self._session = session
                self._user_repo = UserRepository(User, session)
                break
    
    def _serialize_user_data(self, user: User) -> Dict[str, Any]:
        """Convert user model to API-ready format."""
        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "company": user.company,
            "role": user.role,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "phone": user.phone,
            "timezone": user.timezone,
            "language": getattr(user, 'language', 'en'),  # Safe fallback
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
        }
    
    async def create_or_update_user_from_google(
        self, 
        google_user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create or update user from Google OAuth data.
        
        Args:
            google_user_data: User data from Google OAuth
            
        Returns:
            User data with tokens
        """
        await self._ensure_repo()
        
        email = google_user_data["email"]
        google_id = google_user_data["id"]
        
        # Start a transaction
        async with self._session.begin():
            # Check if user exists
            existing_user = await self._user_repo.get_by_email(email)
            
            if existing_user:
                # Update existing user
                user = await self._update_user_google_info(
                    existing_user.id, 
                    google_user_data
                )
            else:
                # Create new user
                user = await self._create_user_from_google(google_user_data)
            
            # Store/update OAuth provider info
            await self._store_oauth_provider_info(
                user.id, 
                "google", 
                google_user_data
            )
            
            # Update last login
            await self._user_repo.update_last_login(user.id)
        
        # Generate tokens
        user_data = self._serialize_user_data(user)
        tokens = self.jwt_service.create_token_pair(
            user_id=str(user.id),
            additional_claims={
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
        )
        
        return {
            "user": user_data,
            "tokens": tokens
        }
    
    async def _create_user_from_google(
        self, 
        google_user_data: Dict[str, Any]
    ) -> User:
        """Create new user from Google OAuth data."""
        return await self._user_repo.create(
            email=google_user_data["email"],
            email_verified=google_user_data.get("email_verified", False),
            name=google_user_data.get("name", ""),
            avatar_url=google_user_data.get("picture", ""),
            locale=google_user_data.get("locale", "en"),
            role="user",
            is_active=True,
            metadata={
                "oauth_provider": "google",
                "google_id": google_user_data["id"]
            }
        )
    
    async def _update_user_google_info(
        self, 
        user_id: UUID, 
        google_user_data: Dict[str, Any]
    ) -> User:
        """Update existing user with Google OAuth data."""
        return await self._user_repo.update(
            user_id,
            name=google_user_data.get("name"),
            avatar_url=google_user_data.get("picture"),
            email_verified=google_user_data.get("email_verified", False)
        )
    
    async def _store_oauth_provider_info(
        self, 
        user_id: UUID, 
        provider: str, 
        provider_data: Dict[str, Any]
    ) -> None:
        """Store or update OAuth provider information."""
        # Check if provider record exists
        existing = await self._session.execute(
            select(OAuthProvider).where(
                OAuthProvider.user_id == user_id,
                OAuthProvider.provider == provider
            )
        )
        oauth_provider = existing.scalar_one_or_none()
        
        if oauth_provider:
            # Update existing record
            oauth_provider.provider_data = provider_data
            oauth_provider.updated_at = datetime.utcnow()
        else:
            # Create new record
            oauth_provider = OAuthProvider(
                user_id=user_id,
                provider=provider,
                provider_user_id=provider_data["id"],
                provider_email=provider_data["email"],
                provider_data=provider_data
            )
            self._session.add(oauth_provider)
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address."""
        await self._ensure_repo()
        
        user = await self._user_repo.get_by_email(email)
        return self._serialize_user_data(user) if user else None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        await self._ensure_repo()
        
        try:
            user_uuid = UUID(user_id)
            user = await self._user_repo.get(user_uuid)
            return self._serialize_user_data(user) if user else None
        except ValueError:
            return None
    
    async def search_users(
        self, 
        query: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search users by name, email, or company."""
        await self._ensure_repo()
        
        users = await self._user_repo.search_users(query, skip, limit)
        return [self._serialize_user_data(user) for user in users]
    
    async def get_active_users(
        self, 
        days: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recently active users."""
        await self._ensure_repo()
        
        users = await self._user_repo.get_active_users(days, skip, limit)
        return [self._serialize_user_data(user) for user in users]
    
    async def update_user_profile(
        self,
        user_id: str,
        **update_data
    ) -> Optional[Dict[str, Any]]:
        """Update user profile information."""
        await self._ensure_repo()
        
        try:
            user_uuid = UUID(user_id)
            
            # Filter out None values and invalid fields
            allowed_fields = {
                'name', 'company', 'phone', 'timezone', 
                'language', 'avatar_url', 'metadata'
            }
            
            filtered_data = {
                k: v for k, v in update_data.items() 
                if k in allowed_fields and v is not None
            }
            
            if not filtered_data:
                return await self.get_user_by_id(user_id)
            
            user = await self._user_repo.update(user_uuid, **filtered_data)
            return self._serialize_user_data(user) if user else None
            
        except ValueError:
            return None
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account."""
        await self._ensure_repo()
        
        try:
            user_uuid = UUID(user_id)
            user = await self._user_repo.deactivate_user(user_uuid)
            return user is not None
        except ValueError:
            return False
    
    async def reactivate_user(self, user_id: str) -> bool:
        """Reactivate a user account."""
        await self._ensure_repo()
        
        try:
            user_uuid = UUID(user_id)
            user = await self._user_repo.reactivate_user(user_uuid)
            return user is not None
        except ValueError:
            return False
    
    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics."""
        await self._ensure_repo()
        
        return await self._user_repo.get_user_statistics()
    
    async def get_users_by_role(
        self,
        role: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get users by role."""
        await self._ensure_repo()
        
        users = await self._user_repo.get_users_by_role(role, skip, limit)
        return [self._serialize_user_data(user) for user in users]
    
    async def verify_user_access(
        self,
        user_id: str,
        required_role: Optional[str] = None
    ) -> bool:
        """Verify user access and optional role requirement."""
        user = await self.get_user_by_id(user_id)
        
        if not user or not user['is_active']:
            return False
        
        if required_role and user['role'] != required_role:
            return False
        
        return True
    
    async def create_user_from_google(self, google_user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user from Google OAuth data (for testing compatibility)."""
        await self._ensure_repo()
        
        user = await self._create_user_from_google(google_user_data)
        return self._serialize_user_data(user)
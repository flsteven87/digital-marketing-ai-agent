"""OAuth provider repository for managing OAuth provider data access."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_

from app.repositories.base import BaseRepository
from app.models.user import OAuthProvider


class OAuthProviderRepository(BaseRepository[OAuthProvider]):
    """Repository for OAuth provider-specific database operations."""
    
    async def get_by_provider_and_user(
        self, 
        user_id: UUID, 
        provider: str
    ) -> Optional[OAuthProvider]:
        """Get OAuth provider by user ID and provider name.
        
        Args:
            user_id: User's UUID
            provider: OAuth provider name (e.g., 'google')
            
        Returns:
            OAuthProvider instance or None
        """
        return await self.get_by(
            user_id=user_id,
            provider=provider
        )
    
    async def get_by_provider_user_id(
        self, 
        provider: str, 
        provider_user_id: str
    ) -> Optional[OAuthProvider]:
        """Get OAuth provider by provider name and external user ID.
        
        Args:
            provider: OAuth provider name (e.g., 'google')
            provider_user_id: User ID from the OAuth provider
            
        Returns:
            OAuthProvider instance or None
        """
        return await self.get_by(
            provider=provider,
            provider_user_id=provider_user_id
        )
    
    async def get_user_providers(self, user_id: UUID) -> List[OAuthProvider]:
        """Get all OAuth providers for a user.
        
        Args:
            user_id: User's UUID
            
        Returns:
            List of OAuth providers
        """
        return await self.get_all(user_id=user_id)
    
    async def create_or_update_provider(
        self,
        user_id: UUID,
        provider: str,
        provider_user_id: str,
        provider_email: Optional[str] = None,
        provider_data: Optional[Dict[str, Any]] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_expires_at: Optional[datetime] = None
    ) -> OAuthProvider:
        """Create or update OAuth provider information.
        
        Args:
            user_id: User's UUID
            provider: OAuth provider name
            provider_user_id: User ID from the OAuth provider
            provider_email: Email from the OAuth provider
            provider_data: Additional provider data
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            token_expires_at: Token expiration time
            
        Returns:
            OAuth provider instance
        """
        # Check if provider already exists
        existing = await self.get_by_provider_and_user(user_id, provider)
        
        if existing:
            # Update existing provider
            return await self.update(
                existing.id,
                provider_user_id=provider_user_id,
                provider_email=provider_email,
                provider_data=provider_data or {},
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=token_expires_at,
                updated_at=datetime.utcnow()
            )
        else:
            # Create new provider
            return await self.create(
                user_id=user_id,
                provider=provider,
                provider_user_id=provider_user_id,
                provider_email=provider_email,
                provider_data=provider_data or {},
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=token_expires_at
            )
    
    async def update_tokens(
        self,
        provider_id: UUID,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expires_at: Optional[datetime] = None
    ) -> Optional[OAuthProvider]:
        """Update OAuth tokens for a provider.
        
        Args:
            provider_id: OAuth provider UUID
            access_token: New access token
            refresh_token: New refresh token
            token_expires_at: Token expiration time
            
        Returns:
            Updated OAuth provider or None
        """
        return await self.update(
            provider_id,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=token_expires_at,
            updated_at=datetime.utcnow()
        )
    
    async def delete_provider(self, user_id: UUID, provider: str) -> bool:
        """Delete OAuth provider for a user.
        
        Args:
            user_id: User's UUID
            provider: OAuth provider name
            
        Returns:
            True if deleted, False otherwise
        """
        existing = await self.get_by_provider_and_user(user_id, provider)
        if existing:
            return await self.delete(existing.id)
        return False
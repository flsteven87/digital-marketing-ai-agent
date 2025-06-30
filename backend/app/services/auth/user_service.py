"""User management service with OAuth integration using direct PostgreSQL."""

import json
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from app.core.postgres import get_postgres
from app.core.database import get_db_session
from app.models.user import User as UserModel, OAuthProvider
from app.services.auth.jwt_service import JWTService
from app.core.exceptions import AuthenticationError, UserNotFoundError


class UserService:
    """User management with OAuth and JWT integration."""
    
    def __init__(self):
        self.jwt_service = JWTService()
    
    def _serialize_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert database types to API-ready format."""
        return {
            **user_data,
            "id": str(user_data["id"]),
            "created_at": user_data["created_at"].isoformat(),
            "updated_at": user_data["updated_at"].isoformat(),
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
        db = await get_postgres()
        
        # Generate UUID for the user
        from uuid import uuid4
        user_id = str(uuid4())
        
        query = """
            INSERT INTO public.users (
                id, email, email_verified, name, avatar_url, locale, 
                role, is_active, metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            user_id,
            google_user_data["email"],
            google_user_data.get("email_verified", False),
            google_user_data.get("name", ""),
            google_user_data.get("picture", ""),
            google_user_data.get("locale", "en"),
            "user",
            True,
            json.dumps({
                "oauth_provider": "google",
                "google_id": google_user_data["id"]
            })
        )
        
        result = await db.execute_insert(query, params)
        return self._serialize_user_data(result)
    
    async def update_user_google_info(self, user_id: str, google_user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing user with Google OAuth data."""
        db = await get_postgres()
        
        query = """
            UPDATE public.users SET
                name = %s,
                avatar_url = %s,
                email_verified = %s,
                last_login_at = NOW(),
                updated_at = NOW()
            WHERE id = %s
        """
        
        params = (
            google_user_data.get("name", ""),
            google_user_data.get("picture", ""),
            google_user_data.get("email_verified", False),
            user_id
        )
        
        result = await db.execute_update(query, params)
        return self._serialize_user_data(result)
    
    async def store_oauth_provider_info(self, user_id: str, provider: str, provider_data: Dict[str, Any]) -> None:
        """Store or update OAuth provider information."""
        db = await get_postgres()
        
        # Check if provider record exists
        check_query = "SELECT id FROM public.oauth_providers WHERE user_id = %s AND provider = %s"
        existing = await db.execute_query(check_query, (user_id, provider))
        
        if existing:
            # Update existing record
            update_query = """
                UPDATE public.oauth_providers SET
                    provider_data = %s, updated_at = NOW()
                WHERE user_id = %s AND provider = %s
            """
            await db.execute_update(update_query, (json.dumps(provider_data), user_id, provider))
        else:
            # Insert new record
            oauth_id = str(uuid4())
            insert_query = """
                INSERT INTO public.oauth_providers (
                    id, user_id, provider, provider_user_id, provider_email, provider_data
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (oauth_id, user_id, provider, provider_data["id"], provider_data["email"], json.dumps(provider_data))
            await db.execute_insert(insert_query, params)
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address."""
        db = await get_postgres()
        query = "SELECT * FROM public.users WHERE email = %s AND is_active = true"
        results = await db.execute_query(query, (email,))
        return results[0] if results else None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        db = await get_postgres()
        query = "SELECT * FROM public.users WHERE id = %s AND is_active = true"
        results = await db.execute_query(query, (user_id,))
        return results[0] if results else None
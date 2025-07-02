"""Google OAuth 2.0 service implementation using modern best practices."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
import httpx
from authlib.integrations.requests_client import OAuth2Session
from authlib.common.errors import AuthlibBaseError
import redis.asyncio as redis

from app.core.config import settings
from app.core.exceptions import AuthenticationError


class GoogleOAuthService:
    """Google OAuth 2.0 service with secure implementation."""
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET.get_secret_value() if settings.GOOGLE_CLIENT_SECRET else None
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.is_configured = bool(self.client_id and self.client_secret)
        
        # Google OAuth 2.0 endpoints
        self.authorization_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        # OAuth scopes
        self.scope = ["openid", "email", "profile"]
        
        # Redis client for state management
        self.redis_client = None
        self.state_expiry = 600  # 10 minutes
        
        # In-memory fallback for development when Redis is not available
        self._memory_store = {}
        self._use_memory_store = False

    async def _get_redis_client(self):
        """Get Redis client connection with fallback to memory store."""
        if not self.redis_client and not self._use_memory_store:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL)
                # Test connection
                await self.redis_client.ping()
            except Exception:
                # Fall back to in-memory store for development
                self._use_memory_store = True
                print("⚠️  Redis not available, using in-memory store for OAuth state (development only)")
        return self.redis_client

    async def _store_oauth_state(self, state: str, session_data: Dict):
        """Store OAuth state in Redis or memory store."""
        if self._use_memory_store:
            # Store in memory with expiration
            expiry_time = datetime.now() + timedelta(seconds=self.state_expiry)
            self._memory_store[state] = {
                **session_data,
                'created_at': datetime.now().isoformat(),
                'expires_at': expiry_time.isoformat()
            }
        else:
            redis_client = await self._get_redis_client()
            key = f"oauth_state:{state}"
            await redis_client.setex(
                key, 
                self.state_expiry, 
                json.dumps({
                    **session_data,
                    'created_at': datetime.now().isoformat()
                })
            )

    async def _get_oauth_state(self, state: str) -> Optional[Dict]:
        """Retrieve OAuth state from Redis or memory store."""
        if self._use_memory_store:
            # Get from memory store
            data = self._memory_store.get(state)
            if data:
                # Check expiration
                expires_at = datetime.fromisoformat(data['expires_at'])
                if datetime.now() < expires_at:
                    # Clean up after use
                    del self._memory_store[state]
                    # Remove expires_at before returning
                    data.pop('expires_at', None)
                    return data
                else:
                    # Expired, clean up
                    del self._memory_store[state]
            return None
        else:
            redis_client = await self._get_redis_client()
            key = f"oauth_state:{state}"
            data = await redis_client.get(key)
            if data:
                await redis_client.delete(key)  # Clean up after use
                return json.loads(data)
            return None
        
    async def get_authorization_url(self, state: str = None) -> tuple[str, str]:
        """Generate Google OAuth authorization URL with proper session management."""
        client = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        )
        
        # Generate authorization URL with forced consent
        authorization_url, generated_state = client.create_authorization_url(
            self.authorization_url,
            state=state,
            prompt='consent',  # Force consent screen
            access_type='offline'  # Request refresh token
        )
        
        # Store the session data in Redis for later token exchange
        session_data = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope
        }
        
        await self._store_oauth_state(generated_state, session_data)
        
        return authorization_url, generated_state
    
    async def exchange_code_for_token(self, code: str, state: str = None) -> Dict:
        """Exchange authorization code for access token using stored session."""
        if not state:
            raise AuthenticationError("Missing OAuth state parameter")
            
        # Retrieve the stored OAuth session data from Redis
        session_data = await self._get_oauth_state(state)
        if not session_data:
            raise AuthenticationError("Invalid or expired OAuth state")
        
        # Create a new OAuth client with the stored session data
        client = OAuth2Session(
            client_id=session_data['client_id'],
            redirect_uri=session_data['redirect_uri'],
            scope=session_data['scope']
        )
        
        # Exchange code for token
        try:
            token = await asyncio.to_thread(
                client.fetch_token,
                self.token_url,
                code=code,
                client_secret=self.client_secret,
                include_client_id=True
            )
        except Exception as e:
            raise AuthenticationError(f"Token exchange failed: {str(e)}")
        
        return {
            "access_token": token["access_token"],
            "token_type": token.get("token_type", "Bearer"),
            "expires_in": token.get("expires_in"),
            "refresh_token": token.get("refresh_token"),
            "scope": token.get("scope"),
            "id_token": token.get("id_token")
        }
    
    async def get_user_info(self, access_token: str) -> Dict:
        """Get user information from Google."""
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(self.userinfo_url, headers=headers)
            response.raise_for_status()
            
            user_data = response.json()
            
            return {
                "id": user_data["id"],
                "email": user_data["email"],
                "name": user_data.get("name", ""),
                "given_name": user_data.get("given_name", ""),
                "family_name": user_data.get("family_name", ""),
                "picture": user_data.get("picture", ""),
                "email_verified": user_data.get("verified_email", False),
                "locale": user_data.get("locale", "en")
            }
    
    async def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh access token using refresh token."""
        async with httpx.AsyncClient() as client:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }
            
            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            return {
                "access_token": token_data["access_token"],
                "token_type": token_data.get("token_type", "Bearer"),
                "expires_in": token_data.get("expires_in"),
                "scope": token_data.get("scope")
            }
    
    def validate_token(self, access_token: str) -> bool:
        """Validate if access token is still valid."""
        try:
            validation_url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
            with httpx.Client() as client:
                response = client.get(validation_url)
                return response.status_code == 200
        except Exception:
            return False
"""Google OAuth 2.0 service implementation using modern best practices."""

import asyncio
from datetime import datetime
from typing import Dict, Optional
import httpx
from authlib.integrations.requests_client import OAuth2Session
from authlib.common.errors import AuthlibBaseError

from app.core.config import settings
from app.core.exceptions import AuthenticationError


class GoogleOAuthService:
    """Google OAuth 2.0 service with secure implementation."""
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.is_configured = bool(self.client_id and self.client_secret)
        
        # Google OAuth 2.0 endpoints
        self.authorization_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        # OAuth scopes
        self.scope = ["openid", "email", "profile"]
        
        # Store sessions for proper state management
        self._sessions = {}
    
    def get_authorization_url(self, state: str = None) -> tuple[str, str]:
        """Generate Google OAuth authorization URL with proper session management."""
        client = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        )
        
        # Generate authorization URL
        authorization_url, generated_state = client.create_authorization_url(
            self.authorization_url,
            state=state
        )
        
        # Store the session for later token exchange
        self._sessions[generated_state] = {
            'client': client,
            'created_at': datetime.now()
        }
        
        return authorization_url, generated_state
    
    async def exchange_code_for_token(self, code: str, state: str = None) -> Dict:
        """Exchange authorization code for access token using stored session."""
        if not state or state not in self._sessions:
            raise AuthenticationError("Invalid or expired OAuth state")
        
        # Retrieve the stored OAuth session
        session_data = self._sessions[state]
        client = session_data['client']
        
        # Clean up the stored session
        del self._sessions[state]
        
        # Exchange code for token using the original session
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
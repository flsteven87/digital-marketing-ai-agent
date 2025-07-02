from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import secrets

from app.services.auth.jwt_service import JWTService
from app.schemas.auth import (
    Token, UserRegister, GoogleOAuthRequest, LoginResponse,
    AuthorizationUrlResponse, TokenResponse, UserProfile, RefreshTokenRequest
)
from app.schemas.user import User, UserCreate
from app.services.auth.user_service import UserService
from app.services.auth.google_oauth import GoogleOAuthService
from app.core.exceptions import AuthenticationError
from app.api.deps import get_current_user

router = APIRouter()

# Initialize OAuth services
google_oauth = GoogleOAuthService()


@router.get("/google/authorize", response_model=AuthorizationUrlResponse)
async def google_authorize() -> Any:
    """Get Google OAuth authorization URL."""
    if not google_oauth.is_configured:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )
    
    state = secrets.token_urlsafe(32)
    authorization_url, _ = await google_oauth.get_authorization_url(state=state)
    
    return AuthorizationUrlResponse(
        authorization_url=authorization_url,
        state=state
    )


@router.post("/google/callback", response_model=LoginResponse)
async def google_callback(request: GoogleOAuthRequest) -> Any:
    """Handle Google OAuth callback."""
    if not google_oauth.is_configured:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )
    
    try:
        # Exchange code for token
        token_data = await google_oauth.exchange_code_for_token(
            code=request.code,
            state=request.state
        )
        
        # Get user info
        user_info = await google_oauth.get_user_info(token_data["access_token"])
        
        # Create or update user using async context manager
        async with UserService() as user_service:
            auth_result = await user_service.create_or_update_user_from_google(user_info)
        
        return LoginResponse(
            user=UserProfile(**auth_result["user"]),
            tokens=TokenResponse(**auth_result["tokens"])
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/providers")
async def get_oauth_providers() -> dict:
    """Get available OAuth providers."""
    return {
        "providers": [
            {
                "name": "google",
                "display_name": "Google", 
                "enabled": google_oauth.is_configured,
                "authorize_endpoint": "/auth/google/authorize"
            }
        ]
    }


@router.post("/register", response_model=User)
async def register(user_data: UserRegister) -> Any:
    """Register a new user."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Please use OAuth for registration"
    )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """Login with email and password."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Please use OAuth for authentication"
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest) -> Any:
    """Refresh access token using refresh token."""
    try:
        jwt_service = JWTService()
        refresh_token = request.refresh_token
        
        # Verify refresh token
        payload = jwt_service.verify_token(refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Generate new token pair
        tokens = jwt_service.create_token_pair(user_id)
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)) -> Any:
    """Get current user information."""
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)) -> dict:
    """Logout current user."""
    return {"message": "Successfully logged out"}
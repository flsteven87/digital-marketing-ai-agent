from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError

from app.core import security
from app.core.config import settings
from app.core.database import get_db_session
from app.schemas.user import User
from app.models.user import User as UserModel

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def _convert_user_model_to_schema(user: UserModel) -> User:
    """Convert SQLAlchemy User model to Pydantic User schema."""
    return User(
        id=user.id,
        email=user.email,
        email_verified=user.email_verified,
        name=user.name,
        avatar_url=user.avatar_url,
        company=user.company,
        role=user.role,
        phone=user.phone,
        timezone=user.timezone or "UTC",
        locale=user.locale or "en",
        is_active=user.is_active,
        metadata=user.user_metadata or {},
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = security.decode_token(token)
        if payload.type != "access":
            raise credentials_exception
        user_id: str = payload.sub
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValidationError):
        raise credentials_exception
    
    # Get user from database using SQLAlchemy
    db = get_db_session()
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise credentials_exception
        
        return _convert_user_model_to_schema(user)
    finally:
        db.close()


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
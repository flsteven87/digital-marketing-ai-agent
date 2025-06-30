from typing import Generator, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core import security
from app.core.config import settings
from app.core.database_async import get_async_db
from app.repositories.user import UserRepository
from app.schemas.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)




async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
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
    
    # Use unified repository pattern
    from app.models.user import User as UserModel
    user_repo = UserRepository(UserModel, db)
    user = await user_repo.get(UUID(user_id))
    
    if not user:
        raise credentials_exception
    
    # Convert to Pydantic schema
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
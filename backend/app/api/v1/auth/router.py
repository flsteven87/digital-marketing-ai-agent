from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core import security
from app.core.config import settings
from app.schemas.auth import Token, UserLogin, UserRegister
from app.schemas.user import User, UserCreate
from app.services.auth import auth_service
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/register", response_model=User)
async def register(
    user_data: UserRegister
) -> Any:
    user = await auth_service.create_user(UserCreate(**user_data.dict()))
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = await auth_service.authenticate(
        email=form_data.username,
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = security.create_access_token(user.id)
    refresh_token = security.create_refresh_token(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str
) -> Any:
    try:
        payload = security.decode_token(refresh_token)
        if payload.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user = await auth_service.get_user(payload.sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        access_token = security.create_access_token(user.id)
        new_refresh_token = security.create_refresh_token(user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    # In a real implementation, you might want to blacklist the token
    return {"message": "Successfully logged out"}
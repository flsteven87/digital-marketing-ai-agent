from typing import Any, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.social import (
    SocialAccount,
    SocialPost,
    PostSchedule,
    PlatformCredentials
)
from app.schemas.user import User
from app.services.social_media.social_service import SocialMediaService
from app.api.deps import get_current_user

router = APIRouter()
social_service = SocialMediaService()


@router.post("/accounts/connect")
async def connect_social_account(
    credentials: PlatformCredentials,
    current_user: User = Depends(get_current_user)
) -> Any:
    account = await social_service.connect_account(
        user_id=current_user.id,
        platform=credentials.platform,
        credentials=credentials.credentials
    )
    return account


@router.get("/accounts", response_model=List[SocialAccount])
async def get_connected_accounts(
    current_user: User = Depends(get_current_user)
) -> Any:
    accounts = await social_service.get_user_accounts(current_user.id)
    return accounts


@router.delete("/accounts/{account_id}")
async def disconnect_social_account(
    account_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    await social_service.disconnect_account(
        account_id=account_id,
        user_id=current_user.id
    )
    return {"message": "Account disconnected successfully"}


@router.post("/posts/publish")
async def publish_post(
    post: SocialPost,
    current_user: User = Depends(get_current_user)
) -> Any:
    result = await social_service.publish_post(
        user_id=current_user.id,
        post=post
    )
    return result


@router.post("/posts/schedule")
async def schedule_post(
    schedule: PostSchedule,
    current_user: User = Depends(get_current_user)
) -> Any:
    scheduled_post = await social_service.schedule_post(
        user_id=current_user.id,
        schedule=schedule
    )
    return scheduled_post


@router.get("/posts/scheduled")
async def get_scheduled_posts(
    current_user: User = Depends(get_current_user),
    start_date: datetime = None,
    end_date: datetime = None,
    platform: str = None
) -> Any:
    posts = await social_service.get_scheduled_posts(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        platform=platform
    )
    return posts


@router.put("/posts/scheduled/{post_id}")
async def update_scheduled_post(
    post_id: str,
    updates: dict,
    current_user: User = Depends(get_current_user)
) -> Any:
    updated_post = await social_service.update_scheduled_post(
        post_id=post_id,
        user_id=current_user.id,
        updates=updates
    )
    return updated_post


@router.delete("/posts/scheduled/{post_id}")
async def cancel_scheduled_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    await social_service.cancel_scheduled_post(
        post_id=post_id,
        user_id=current_user.id
    )
    return {"message": "Scheduled post cancelled successfully"}


@router.get("/posts/history")
async def get_post_history(
    current_user: User = Depends(get_current_user),
    platform: str = None,
    skip: int = 0,
    limit: int = 20
) -> Any:
    posts = await social_service.get_post_history(
        user_id=current_user.id,
        platform=platform,
        skip=skip,
        limit=limit
    )
    return posts


@router.get("/best-times")
async def get_best_posting_times(
    platform: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    best_times = await social_service.get_best_posting_times(
        user_id=current_user.id,
        platform=platform
    )
    return best_times
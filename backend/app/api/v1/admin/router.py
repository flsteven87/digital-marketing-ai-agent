from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.user import User, UserUpdate
from app.schemas.admin import (
    SystemStats,
    UserManagement,
    BrandManagement,
    SubscriptionManagement
)
from app.services.admin.admin_service import AdminService
from app.api.deps import get_current_user, get_admin_user

router = APIRouter()
admin_service = AdminService()


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    admin_user: User = Depends(get_admin_user)
) -> Any:
    stats = await admin_service.get_system_stats()
    return stats


@router.get("/users", response_model=List[UserManagement])
async def list_users(
    admin_user: User = Depends(get_admin_user),
    skip: int = 0,
    limit: int = 50,
    search: str = None,
    status: str = None
) -> Any:
    users = await admin_service.list_users(
        skip=skip,
        limit=limit,
        search=search,
        status=status
    )
    return users


@router.get("/users/{user_id}", response_model=UserManagement)
async def get_user_details(
    user_id: str,
    admin_user: User = Depends(get_admin_user)
) -> Any:
    user = await admin_service.get_user_details(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    admin_user: User = Depends(get_admin_user)
) -> Any:
    updated_user = await admin_service.update_user(user_id, user_update)
    return updated_user


@router.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    reason: str,
    admin_user: User = Depends(get_admin_user)
) -> Any:
    await admin_service.suspend_user(user_id, reason)
    return {"message": "User suspended successfully"}


@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    admin_user: User = Depends(get_admin_user)
) -> Any:
    await admin_service.activate_user(user_id)
    return {"message": "User activated successfully"}


@router.get("/brands", response_model=List[BrandManagement])
async def list_brands(
    admin_user: User = Depends(get_admin_user),
    skip: int = 0,
    limit: int = 50
) -> Any:
    brands = await admin_service.list_brands(skip=skip, limit=limit)
    return brands


@router.get("/subscriptions", response_model=List[SubscriptionManagement])
async def list_subscriptions(
    admin_user: User = Depends(get_admin_user),
    status: str = None,
    plan: str = None
) -> Any:
    subscriptions = await admin_service.list_subscriptions(
        status=status,
        plan=plan
    )
    return subscriptions


@router.post("/subscriptions/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: str,
    reason: str,
    admin_user: User = Depends(get_admin_user)
) -> Any:
    await admin_service.cancel_subscription(subscription_id, reason)
    return {"message": "Subscription cancelled successfully"}


@router.get("/audit-logs")
async def get_audit_logs(
    admin_user: User = Depends(get_admin_user),
    user_id: str = None,
    action: str = None,
    skip: int = 0,
    limit: int = 100
) -> Any:
    logs = await admin_service.get_audit_logs(
        user_id=user_id,
        action=action,
        skip=skip,
        limit=limit
    )
    return logs


@router.post("/broadcast")
async def send_broadcast_message(
    subject: str,
    message: str,
    target: str = "all",
    admin_user: User = Depends(get_admin_user)
) -> Any:
    result = await admin_service.send_broadcast(
        subject=subject,
        message=message,
        target=target
    )
    return result
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.content import router as content_router
from app.api.v1.social import router as social_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter()

api_router.include_router(auth_router.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat_router.router, prefix="/chat", tags=["chat"])
api_router.include_router(content_router.router, prefix="/content", tags=["content"])
api_router.include_router(social_router.router, prefix="/social", tags=["social"])
api_router.include_router(analytics_router.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(admin_router.router, prefix="/admin", tags=["admin"])
from fastapi import APIRouter
from app.api.v1.chat import router as chat_router

api_router = APIRouter()

# 只包含 chat 路由用於 POC 測試
api_router.include_router(chat_router.router, prefix="/chat", tags=["chat"])
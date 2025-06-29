from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserModel(BaseModel):
    id: UUID
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None
    role: str = "user"
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    timezone: str = "Asia/Taipei"
    language: str = "zh-TW"
    is_active: bool = True
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
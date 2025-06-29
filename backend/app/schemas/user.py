from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: str
    name: str
    company: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: str
    is_active: bool = True
    role: str = "user"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
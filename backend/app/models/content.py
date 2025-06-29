from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from uuid import UUID


class GeneratedContentModel(BaseModel):
    id: UUID
    user_id: UUID
    brand_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    content_type: str  # 'social_post', 'blog', 'email', 'ad_copy'
    platform: List[str] = []
    title: Optional[str] = None
    content: str
    media_urls: List[str] = []
    hashtags: List[str] = []
    metadata: Dict[str, Any] = {}
    status: str = "draft"  # 'draft', 'scheduled', 'published', 'failed'
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BrandModel(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    brand_voice: Optional[str] = None
    brand_values: List[str] = []
    color_palette: Dict[str, Any] = {}
    social_profiles: Dict[str, Any] = {}
    settings: Dict[str, Any] = {}
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
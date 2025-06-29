from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.content import (
    ContentGeneration,
    ContentRequest,
    ContentTemplate,
    GeneratedContent
)
from app.schemas.user import User
from app.services.ai.content_service import ContentService
from app.api.deps import get_current_user

router = APIRouter()
content_service = ContentService()


@router.post("/generate", response_model=GeneratedContent)
async def generate_content(
    request: ContentRequest,
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        content = await content_service.generate_content(
            user_id=current_user.id,
            brand_id=request.brand_id,
            content_type=request.content_type,
            platform=request.platform,
            prompt=request.prompt,
            tone=request.tone,
            keywords=request.keywords
        )
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-batch", response_model=List[GeneratedContent])
async def generate_batch_content(
    requests: List[ContentRequest],
    current_user: User = Depends(get_current_user)
) -> Any:
    contents = await content_service.generate_batch_content(
        user_id=current_user.id,
        requests=requests
    )
    return contents


@router.get("/templates", response_model=List[ContentTemplate])
async def get_content_templates(
    content_type: str = None,
    platform: str = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    templates = await content_service.get_templates(
        content_type=content_type,
        platform=platform
    )
    return templates


@router.post("/save")
async def save_content(
    content: GeneratedContent,
    current_user: User = Depends(get_current_user)
) -> Any:
    saved_content = await content_service.save_content(
        user_id=current_user.id,
        content=content
    )
    return {"message": "Content saved successfully", "id": saved_content.id}


@router.get("/history")
async def get_content_history(
    current_user: User = Depends(get_current_user),
    brand_id: str = None,
    content_type: str = None,
    skip: int = 0,
    limit: int = 20
) -> Any:
    contents = await content_service.get_user_contents(
        user_id=current_user.id,
        brand_id=brand_id,
        content_type=content_type,
        skip=skip,
        limit=limit
    )
    return contents


@router.put("/{content_id}")
async def update_content(
    content_id: str,
    updates: dict,
    current_user: User = Depends(get_current_user)
) -> Any:
    updated_content = await content_service.update_content(
        content_id=content_id,
        user_id=current_user.id,
        updates=updates
    )
    return updated_content


@router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    await content_service.delete_content(
        content_id=content_id,
        user_id=current_user.id
    )
    return {"message": "Content deleted successfully"}
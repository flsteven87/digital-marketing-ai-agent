from typing import Any
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import json

from app.schemas.chat import ChatMessage, ChatSession, ChatRequest, ChatResponse
from app.schemas.user import User
from app.services.ai.chat_service import ChatService
from app.api.deps import get_current_user

router = APIRouter()
chat_service = ChatService()


@router.post("/sessions", response_model=ChatSession)
async def create_chat_session(
    current_user: User = Depends(get_current_user)
) -> Any:
    session = await chat_service.create_session(user_id=current_user.id)
    return session


@router.get("/sessions")
async def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10
) -> Any:
    sessions = await chat_service.get_user_sessions(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return sessions


@router.get("/sessions/{session_id}/messages")
async def get_chat_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50
) -> Any:
    messages = await chat_service.get_session_messages(
        session_id=session_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return messages


@router.post("/message")
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    async def generate():
        async for chunk in chat_service.process_message_stream(
            session_id=request.session_id,
            message=request.message,
            user_id=current_user.id
        ):
            yield f"data: {json.dumps(chunk)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


@router.post("/message/simple", response_model=ChatResponse)
async def send_simple_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Simple non-streaming chat endpoint for testing"""
    response = await chat_service.process_message(
        session_id=request.session_id,
        message=request.message,
        user_id=current_user.id
    )
    return ChatResponse(message=response, session_id=request.session_id)


@router.post("/test", response_model=ChatResponse)
async def test_chat(
    request: ChatRequest
) -> Any:
    """Test endpoint without authentication for POC"""
    response = await chat_service.process_message(
        session_id=request.session_id,
        message=request.message,
        user_id="test_user"
    )
    return ChatResponse(message=response, session_id=request.session_id)


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str
):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            async for chunk in chat_service.process_message_stream(
                session_id=session_id,
                message=message["content"],
                user_id=message.get("user_id")
            ):
                await websocket.send_json(chunk)
                
    except WebSocketDisconnect:
        await chat_service.disconnect_session(session_id)
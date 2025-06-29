from typing import Any, AsyncGenerator
from uuid import UUID, uuid4
from app.services.ai.base_agent import BaseAgent
from app.services.database.chat_service import ChatDatabaseService


class ChatService:
    def __init__(self):
        self.agent = BaseAgent()
        self.db_service = ChatDatabaseService()
    
    async def create_session(self, user_id: str) -> dict:
        try:
            user_uuid = UUID(user_id)
            session = await self.db_service.create_session(user_uuid)
            return {
                "session_id": str(session.id),
                "user_id": user_id,
                "title": session.title,
                "created_at": session.created_at.isoformat()
            }
        except Exception as e:
            # Fallback for demo/test users
            return {"session_id": f"demo_{uuid4()}", "user_id": user_id}
    
    async def get_user_sessions(self, user_id: str, skip: int = 0, limit: int = 10) -> list:
        try:
            user_uuid = UUID(user_id)
            sessions = await self.db_service.get_user_sessions(user_uuid, skip, limit)
            return [{
                "id": str(session.id),
                "title": session.title,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat()
            } for session in sessions]
        except Exception:
            return []
    
    async def get_session_messages(self, session_id: str, user_id: str, skip: int = 0, limit: int = 50) -> list:
        try:
            session_uuid = UUID(session_id)
            user_uuid = UUID(user_id)
            messages = await self.db_service.get_session_messages(session_uuid, user_uuid, skip, limit)
            return [{
                "id": str(message.id),
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat()
            } for message in messages]
        except Exception:
            return []
    
    async def process_message_stream(self, session_id: str, message: str, user_id: str) -> AsyncGenerator[dict, None]:
        """Stream chat response using LangGraph agent"""
        async for chunk in self.agent.stream(message, session_id):
            if "error" in chunk:
                yield {"type": "error", "content": chunk["error"]}
            else:
                # Extract content from LangGraph chunk
                if "messages" in chunk and chunk["messages"]:
                    last_msg = chunk["messages"][-1]
                    if hasattr(last_msg, 'content') and last_msg.content:
                        yield {"type": "message", "content": last_msg.content}
    
    async def process_message(self, session_id: str, message: str, user_id: str) -> str:
        """Simple message processing for non-streaming requests"""
        try:
            # Save user message
            session_uuid = UUID(session_id)
            await self.db_service.add_message(
                session_uuid, "user", message
            )
            
            # Get AI response
            response = await self.agent.invoke(message, session_id)
            
            # Save AI response
            await self.db_service.add_message(
                session_uuid, "assistant", response
            )
            
            return response
        except Exception as e:
            # Fallback for demo sessions
            return await self.agent.invoke(message, session_id)
    
    async def disconnect_session(self, session_id: str):
        pass
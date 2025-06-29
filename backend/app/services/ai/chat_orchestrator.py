from typing import Any, AsyncGenerator
from uuid import UUID, uuid4
from datetime import datetime
from app.services.ai.base_agent import BaseAgent
from app.services.database.chat_repository import ChatDatabaseService


class ChatService:
    def __init__(self):
        self.agent = BaseAgent()
        self.db_service = ChatDatabaseService()
        self.demo_user_uuid = UUID("00000000-0000-0000-0000-000000000001")
    
    def _get_user_uuid(self, user_id: str) -> UUID:
        """Convert user_id to UUID, handling demo users."""
        return self.demo_user_uuid if user_id == "demo_user" else UUID(user_id)
    
    async def create_session(self, user_id: str, title: str = None) -> dict:
        user_uuid = self._get_user_uuid(user_id)
        title = title or f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        session = await self.db_service.create_session(user_uuid, title=title)
        return {
            "session_id": str(session.id),
            "user_id": user_id,
            "title": session.title,
            "created_at": session.created_at.isoformat()
        }
    
    async def get_user_sessions(self, user_id: str, skip: int = 0, limit: int = 10) -> list:
        user_uuid = self._get_user_uuid(user_id)
        sessions = await self.db_service.get_user_sessions(user_uuid, skip, limit)
        return [{
            "id": str(session.id),
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        } for session in sessions]
    
    async def get_session_messages(self, session_id: str, user_id: str, skip: int = 0, limit: int = 50) -> list:
        try:
            session_uuid = UUID(session_id)
            # Handle demo users with fixed UUID
            if user_id == "demo_user":
                user_uuid = UUID("00000000-0000-0000-0000-000000000001")
            else:
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
        try:
            # Save user message to database first
            session_uuid = UUID(session_id)
            await self.db_service.add_message(session_uuid, "user", message)
            
            # Collect response chunks for saving
            response_chunks = []
            
            async for chunk in self.agent.stream(message, session_id):
                if "error" in chunk:
                    yield {"type": "error", "content": chunk["error"]}
                else:
                    # Extract content from LangGraph chunk
                    if "messages" in chunk and chunk["messages"]:
                        last_msg = chunk["messages"][-1]
                        if hasattr(last_msg, 'content') and last_msg.content:
                            content = last_msg.content
                            response_chunks.append(content)
                            yield {"type": "message", "content": content}
            
            # Save complete response to database
            if response_chunks:
                complete_response = "".join(response_chunks)
                await self.db_service.add_message(session_uuid, "assistant", complete_response)
                
        except Exception as e:
            # Fallback: still stream but don't save to DB
            async for chunk in self.agent.stream(message, session_id):
                if "error" in chunk:
                    yield {"type": "error", "content": chunk["error"]}
                else:
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
    
    async def generate_session_title(self, session_id: str, user_id: str) -> str:
        """Generate a smart title based on the first few messages"""
        try:
            session_uuid = UUID(session_id)
            user_uuid = UUID(user_id)
            
            # Get first few messages
            messages = await self.db_service.get_session_messages(session_uuid, user_uuid, 0, 5)
            
            if not messages:
                return "New Chat"
            
            # Create a prompt to generate title
            conversation_start = " ".join([msg.content for msg in messages[:3]])[:200]
            title_prompt = f"Based on this conversation start, generate a short, descriptive title (max 6 words): {conversation_start}"
            
            title = await self.agent.invoke(title_prompt, session_id)
            # Clean up the title
            title = title.strip().strip('"\'').strip()
            if len(title) > 50:
                title = title[:47] + "..."
            
            # Update the session title
            await self.db_service.update_session_title(session_uuid, user_uuid, title)
            
            return title
        except Exception:
            return "Chat Session"
    
    async def get_or_create_session(self, session_id: str = None, user_id: str = "demo_user") -> dict:
        """Get existing session or create a new one"""
        if session_id and session_id.startswith("demo_"):
            # Handle demo sessions
            return {"session_id": session_id, "user_id": user_id, "title": "Demo Session"}
        
        if session_id:
            try:
                session_uuid = UUID(session_id)
                user_uuid = UUID(user_id)
                session = await self.db_service.get_session(session_uuid, user_uuid)
                if session:
                    return {
                        "session_id": str(session.id),
                        "user_id": user_id,
                        "title": session.title,
                        "created_at": session.created_at.isoformat()
                    }
            except Exception:
                pass
        
        # Create new session if not found
        return await self.create_session(user_id)
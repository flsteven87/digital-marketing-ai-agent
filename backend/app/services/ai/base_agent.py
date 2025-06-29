from typing import Any, Dict, Optional
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage, AIMessage

from app.core.config import settings


class BaseAgent:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7
        )
        self.agent = None
        self._setup_agent()
    
    def _setup_agent(self):
        """Setup basic agent with no tools"""
        system_prompt = "You are a helpful AI marketing assistant. Help users with marketing strategy, content creation, and business growth advice."
        self.agent = create_react_agent(
            model=self.llm,
            tools=[],
            prompt=system_prompt
        )
    
    async def invoke(self, message: str, session_id: str = "default") -> str:
        """Simple invoke method for POC"""
        try:
            config = {"configurable": {"thread_id": session_id}}
            
            response = await self.agent.ainvoke(
                {"messages": [HumanMessage(content=message)]},
                config=config
            )
            
            # Extract the last AI message
            if response and "messages" in response:
                last_message = response["messages"][-1]
                if isinstance(last_message, AIMessage):
                    return last_message.content
            
            return "Sorry, I couldn't process your request."
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def stream(self, message: str, session_id: str = "default"):
        """Stream response for real-time chat"""
        try:
            config = {"configurable": {"thread_id": session_id}}
            
            async for chunk in self.agent.astream(
                {"messages": [HumanMessage(content=message)]},
                config=config
            ):
                yield chunk
                
        except Exception as e:
            yield {"error": str(e)}
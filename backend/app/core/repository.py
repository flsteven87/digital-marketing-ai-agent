"""
Modern async repository pattern for SQLAlchemy 2.0.
Provides type-safe, generic CRUD operations.
"""
from typing import TypeVar, Generic, Optional, List, Dict, Any, Type
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.database_async import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class AsyncRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic async repository with type safety and modern patterns.
    
    Example usage:
        user_repo = AsyncRepository(User, session)
        user = await user_repo.get_by_id(user_id)
    """
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get entity by ID"""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple entities with optional filtering"""
        stmt = select(self.model)
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    stmt = stmt.where(getattr(self.model, key) == value)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create new entity"""
        # Convert Pydantic model to dict, excluding None values
        obj_data = obj_in.model_dump(exclude_unset=True)
        
        # Create SQLAlchemy model instance
        db_obj = self.model(**obj_data)
        
        self.session.add(db_obj)
        await self.session.flush()  # Flush to get the ID
        await self.session.refresh(db_obj)  # Refresh to get computed fields
        
        return db_obj
    
    async def update(
        self, 
        id: UUID, 
        obj_in: UpdateSchemaType
    ) -> Optional[ModelType]:
        """Update existing entity"""
        # Get update data, excluding None values
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if not update_data:
            # No data to update
            return await self.get_by_id(id)
        
        # Perform update
        stmt = update(self.model).where(self.model.id == id).values(**update_data)
        await self.session.execute(stmt)
        
        # Return updated entity
        return await self.get_by_id(id)
    
    async def delete(self, id: UUID) -> bool:
        """Delete entity by ID"""
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        
        return result.rowcount > 0
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filtering"""
        stmt = select(func.count(self.model.id))
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    stmt = stmt.where(getattr(self.model, key) == value)
        
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def exists(self, id: UUID) -> bool:
        """Check if entity exists"""
        stmt = select(func.count(self.model.id)).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar() > 0


class AsyncChatRepository(AsyncRepository):
    """
    Specialized chat repository with relationship loading.
    Extends the generic repository with chat-specific operations.
    """
    
    async def get_user_sessions(
        self, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 10
    ) -> List[ModelType]:
        """Get chat sessions for a user with message count"""
        from app.models.chat import ChatMessage
        
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .where(self.model.is_archived == False)  # noqa
            .order_by(self.model.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_session_with_messages(
        self, 
        session_id: UUID, 
        user_id: UUID
    ) -> Optional[ModelType]:
        """Get session with all messages loaded"""
        stmt = (
            select(self.model)
            .options(selectinload(self.model.messages))
            .where(self.model.id == session_id)
            .where(self.model.user_id == user_id)
            .where(self.model.is_archived == False)  # noqa
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
"""Base repository pattern for data access layer.

This module provides a generic repository pattern that abstracts database operations,
making it easier to switch between different data sources or add caching layers.
"""

from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql import Select

from app.core.database_async import Base

# Type variable for model classes
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository providing basic CRUD operations.
    
    This class implements the repository pattern to abstract database operations
    and provide a clean interface for data access.
    """
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """Initialize repository with model class and database session.
        
        Args:
            model: SQLAlchemy model class
            session: Async database session
        """
        self.model = model
        self.session = session
    
    async def get(self, id: UUID) -> Optional[ModelType]:
        """Get a single record by ID.
        
        Args:
            id: Record UUID
            
        Returns:
            Model instance or None if not found
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by(self, **kwargs) -> Optional[ModelType]:
        """Get a single record by arbitrary fields.
        
        Args:
            **kwargs: Field-value pairs to filter by
            
        Returns:
            First matching model instance or None
        """
        stmt = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None,
        **filters
    ) -> List[ModelType]:
        """Get all records with optional pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field name to order by (prefix with '-' for DESC)
            **filters: Field-value pairs to filter by
            
        Returns:
            List of model instances
        """
        stmt = select(self.model)
        
        # Apply filters
        if filters:
            stmt = stmt.filter_by(**filters)
        
        # Apply ordering
        if order_by:
            if order_by.startswith('-'):
                stmt = stmt.order_by(getattr(self.model, order_by[1:]).desc())
            else:
                stmt = stmt.order_by(getattr(self.model, order_by))
        
        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def count(self, **filters) -> int:
        """Count records with optional filtering.
        
        Args:
            **filters: Field-value pairs to filter by
            
        Returns:
            Number of matching records
        """
        stmt = select(func.count()).select_from(self.model)
        
        if filters:
            stmt = stmt.filter_by(**filters)
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def create(self, **kwargs) -> ModelType:
        """Create a new record.
        
        Args:
            **kwargs: Field values for the new record
            
        Returns:
            Created model instance
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
    
    async def update(self, id: UUID, **kwargs) -> Optional[ModelType]:
        """Update a record by ID.
        
        Args:
            id: Record UUID
            **kwargs: Fields to update
            
        Returns:
            Updated model instance or None if not found
        """
        # Remove None values
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        
        if not update_data:
            return await self.get(id)
        
        # Add updated_at if the model has it
        if hasattr(self.model, 'updated_at'):
            update_data['updated_at'] = datetime.utcnow()
        
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**update_data)
            .returning(self.model)
        )
        
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none()
    
    async def delete(self, id: UUID) -> bool:
        """Delete a record by ID.
        
        Args:
            id: Record UUID
            
        Returns:
            True if deleted, False if not found
        """
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
    
    async def exists(self, **filters) -> bool:
        """Check if a record exists.
        
        Args:
            **filters: Field-value pairs to filter by
            
        Returns:
            True if at least one matching record exists
        """
        stmt = select(func.count()).select_from(self.model).filter_by(**filters)
        result = await self.session.execute(stmt)
        count = result.scalar() or 0
        return count > 0
    
    def _apply_eager_loading(self, stmt: Select, relationships: List[str]) -> Select:
        """Apply eager loading for relationships.
        
        Args:
            stmt: SQLAlchemy select statement
            relationships: List of relationship names to eager load
            
        Returns:
            Modified select statement with eager loading
        """
        for rel in relationships:
            if '.' in rel:
                # Handle nested relationships
                stmt = stmt.options(selectinload(rel))
            else:
                # Handle direct relationships
                stmt = stmt.options(joinedload(getattr(self.model, rel)))
        return stmt
    
    async def get_with_relations(
        self, 
        id: UUID, 
        relationships: List[str]
    ) -> Optional[ModelType]:
        """Get a record with eager-loaded relationships.
        
        Args:
            id: Record UUID
            relationships: List of relationship names to load
            
        Returns:
            Model instance with loaded relationships or None
        """
        stmt = select(self.model).where(self.model.id == id)
        stmt = self._apply_eager_loading(stmt, relationships)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def bulk_create(self, items: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple records in a single operation.
        
        Args:
            items: List of dictionaries with field values
            
        Returns:
            List of created model instances
        """
        instances = [self.model(**item) for item in items]
        self.session.add_all(instances)
        await self.session.flush()
        
        # Refresh to get database-generated values
        for instance in instances:
            await self.session.refresh(instance)
        
        return instances
    
    async def bulk_update(self, updates: List[Dict[str, Any]]) -> int:
        """Update multiple records in a single operation.
        
        Args:
            updates: List of dicts with 'id' and fields to update
            
        Returns:
            Number of records updated
        """
        if not updates:
            return 0
        
        # Add updated_at if the model has it
        if hasattr(self.model, 'updated_at'):
            for update in updates:
                update['updated_at'] = datetime.utcnow()
        
        stmt = update(self.model)
        await self.session.execute(stmt, updates)
        await self.session.flush()
        
        return len(updates)
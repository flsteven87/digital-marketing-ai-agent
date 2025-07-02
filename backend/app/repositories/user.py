"""User repository for managing user data access."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.user_async import User


class UserRepository(BaseRepository[User]):
    """Repository for user-specific database operations."""
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User instance or None
        """
        return await self.get_by(email=email, is_active=True)
    
    async def get_by_oauth_provider(
        self, 
        provider: str, 
        provider_user_id: str
    ) -> Optional[User]:
        """Get user by OAuth provider information.
        
        Args:
            provider: OAuth provider name (e.g., 'google')
            provider_user_id: User ID from the OAuth provider
            
        Returns:
            User instance or None
        """
        stmt = (
            select(User)
            .join(User.oauth_providers)
            .where(
                User.is_active == True,
                User.oauth_providers.any(
                    provider=provider,
                    provider_user_id=provider_user_id
                )
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def search_users(
        self, 
        query: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[User]:
        """Search users by name or email.
        
        Args:
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching users
        """
        search_pattern = f"%{query}%"
        
        stmt = (
            select(User)
            .where(
                User.is_active == True,
                or_(
                    User.name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.company.ilike(search_pattern)
                )
            )
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_active_users(
        self, 
        days: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get users who were active in the last N days.
        
        Args:
            days: Number of days to look back
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active users
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        stmt = (
            select(User)
            .where(
                User.is_active == True,
                User.last_login_at >= cutoff_date
            )
            .order_by(User.last_login_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_last_login(self, user_id: UUID) -> Optional[User]:
        """Update user's last login timestamp.
        
        Args:
            user_id: User's UUID
            
        Returns:
            Updated user instance or None
        """
        return await self.update(
            user_id, 
            last_login_at=datetime.utcnow()
        )
    
    async def get_user_with_providers(self, user_id: UUID) -> Optional[User]:
        """Get user with OAuth providers loaded.
        
        Args:
            user_id: User's UUID
            
        Returns:
            User instance with OAuth providers or None
        """
        return await self.get_with_relations(
            user_id, 
            ['oauth_providers']
        )
    
    async def get_users_by_role(
        self, 
        role: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get users by role.
        
        Args:
            role: User role (e.g., 'admin', 'user')
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of users with the specified role
        """
        return await self.get_all(
            skip=skip,
            limit=limit,
            order_by='-created_at',
            role=role,
            is_active=True
        )
    
    async def deactivate_user(self, user_id: UUID) -> Optional[User]:
        """Deactivate a user account.
        
        Args:
            user_id: User's UUID
            
        Returns:
            Updated user instance or None
        """
        return await self.update(
            user_id,
            is_active=False,
            deactivated_at=datetime.utcnow()
        )
    
    async def reactivate_user(self, user_id: UUID) -> Optional[User]:
        """Reactivate a user account.
        
        Args:
            user_id: User's UUID
            
        Returns:
            Updated user instance or None
        """
        return await self.update(
            user_id,
            is_active=True,
            deactivated_at=None
        )
    
    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics.
        
        Returns:
            Dictionary with user statistics
        """
        total_users = await self.count()
        active_users = await self.count(is_active=True)
        admin_users = await self.count(role='admin', is_active=True)
        
        # Get users created in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_users = await self.session.execute(
            select(func.count())
            .select_from(User)
            .where(User.created_at >= thirty_days_ago)
        )
        new_users_count = new_users.scalar() or 0
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users,
            'new_users_last_30_days': new_users_count,
            'deactivated_users': total_users - active_users
        }
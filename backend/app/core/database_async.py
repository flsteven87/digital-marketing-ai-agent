"""
Modern async SQLAlchemy 2.0 database configuration.
This will gradually replace the legacy database.py
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings


class Base(DeclarativeBase):
    """Modern SQLAlchemy declarative base for 2025"""
    pass


# Create async engine with modern configuration
def create_async_database_engine():
    """Create async engine with optimal configuration for PostgreSQL"""
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")
    
    # Convert to async URL and handle PostgreSQL connection string
    database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    return create_async_engine(
        database_url,
        echo=False,  # Set to True for SQL debugging
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        pool_size=10,        # Number of connections to maintain
        max_overflow=20,     # Additional connections for burst traffic
        # Use NullPool for serverless/testing environments
        poolclass=NullPool if settings.ENVIRONMENT == "test" else None,
        # Disable prepared statement caching for pgbouncer compatibility
        connect_args={"statement_cache_size": 0},
    )


# Create engine and session factory
async_engine = create_async_database_engine()
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Keep objects usable after commit
    autoflush=True,          # Auto-flush before queries
    autocommit=False,        # Explicit transaction control
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session.
    
    Provides automatic transaction management:
    - Commits on success
    - Rollbacks on exception
    - Always closes session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_async_db():
    """Initialize database tables using async engine"""
    async with async_engine.begin() as conn:
        # Import all models to ensure they're registered
        from app.models import user, chat, content  # noqa
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_async_db():
    """Close async engine and all connections"""
    await async_engine.dispose()
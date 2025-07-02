"""
Modern async SQLAlchemy 2.0 database configuration.
This will gradually replace the legacy database.py
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Modern SQLAlchemy declarative base for 2025"""
    pass


# Create async engine with modern configuration
def create_async_database_engine():
    """Create async engine optimized for Supabase Session Mode Pooler"""
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")
    
    # Convert to async URL
    database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    # Optimized configuration for Supabase Session Mode (port 6543)
    # Session mode supports prepared statements and behaves like direct connection
    engine_kwargs = {
        "echo": False,
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 1800,  # 30 minutes for pooler
        "connect_args": {
            "command_timeout": 60,
            "server_settings": {
                "application_name": "digital_marketing_ai_agent"
            }
        }
    }
    
    return create_async_engine(database_url, **engine_kwargs)


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
    
    Provides automatic transaction management with proper async context handling.
    Uses context manager to avoid concurrent session state issues.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_async_db():
    """Initialize database tables using async engine"""
    async with async_engine.begin() as conn:
        # Import all async models to ensure they're registered
        from app.models import async_models  # noqa
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_async_db():
    """Close async engine and all connections"""
    await async_engine.dispose()
"""Database configuration and session management for SQLAlchemy."""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Create SQLAlchemy engine with psycopg 3
engine = create_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://"),
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    pool_size=10,        # Number of connections to maintain
    max_overflow=20,     # Additional connections if needed
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session.
    
    Usage in FastAPI routes:
        @app.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """Get database session for use outside of FastAPI dependency injection."""
    return SessionLocal()


# Legacy Supabase support (to be phased out)
from supabase import create_client, Client
from supabase.client import ClientOptions
from typing import AsyncGenerator


class SupabaseClient:
    """Legacy Supabase client - will be removed in future versions."""
    _instance: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            options = ClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
            )
            cls._instance = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY,
                options=options
            )
        return cls._instance


def get_supabase() -> Client:
    """Legacy function - use get_db() instead."""
    return SupabaseClient.get_client()


async def get_async_supabase() -> AsyncGenerator[Client, None]:
    """Legacy function - use get_db() instead."""
    client = get_supabase()
    try:
        yield client
    finally:
        pass
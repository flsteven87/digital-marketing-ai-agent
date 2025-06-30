"""Database configuration and session management for SQLAlchemy."""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Create SQLAlchemy engine with psycopg 3
if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")
engine = create_engine(
    database_url,
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


# Legacy sync SQLAlchemy - consider migrating to async version
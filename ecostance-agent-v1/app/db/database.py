"""
Database configuration and session management for tenant system.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Database URL - can be configured via environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tenant_system.db")

# Connection pool configuration from environment
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# Create engine with proper connection pooling
if "sqlite" in DATABASE_URL:
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,  # Set to True for SQL query logging
        pool_pre_ping=True  # Verify connections before using them
    )
else:
    # PostgreSQL/Supabase configuration with connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=DB_POOL_SIZE,  # Maximum number of permanent connections
        max_overflow=DB_MAX_OVERFLOW,  # Maximum number of temporary connections
        pool_timeout=DB_POOL_TIMEOUT,  # Timeout for getting a connection from pool
        pool_recycle=DB_POOL_RECYCLE,  # Recycle connections after X seconds
        pool_pre_ping=True,  # Verify connections before using them (prevents stale connections)
        echo=False,  # Set to True for SQL query logging
        # Additional optimizations
        pool_use_lifo=True,  # Use LIFO (Last In First Out) for better connection reuse
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Use with FastAPI Depends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables.
    Call this on application startup.
    """
    Base.metadata.create_all(bind=engine)


def get_db_pool_stats():
    """
    Get database connection pool statistics.
    Useful for monitoring and debugging connection issues.
    
    Returns:
        Dictionary with pool statistics
    """
    try:
        pool = engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow(),
            "max_overflow": DB_MAX_OVERFLOW,
            "configured_pool_size": DB_POOL_SIZE,
            "database_url": DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else "sqlite"
        }
    except Exception as e:
        logger.error(f"Error getting pool stats: {e}")
        return {"error": str(e)}


def close_db_connections():
    """
    Close all database connections.
    Should be called on application shutdown.
    """
    engine.dispose()
    logger.info("✓ Database connections closed")

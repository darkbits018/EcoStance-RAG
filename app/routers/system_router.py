"""
System Monitoring Router - Endpoints for system health and connection pool monitoring.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.auth.dependencies import require_admin
from app.db.database import get_db_pool_stats

router = APIRouter(prefix="/system", tags=["System Monitoring"])


@router.get("/health", response_model=Dict[str, Any])
async def system_health():
    """
    Get system health status.
    
    Returns basic health information about the system.
    """
    return {
        "status": "healthy",
        "service": "RAG Processing API"
    }


@router.get("/pool-stats", response_model=Dict[str, Any])
async def get_pool_stats(
    current_user: dict = Depends(require_admin)
):
    """
    Get connection pool statistics.
    
    Returns detailed information about database connection pool usage.
    Requires admin privileges.
    """
    db_stats = get_db_pool_stats()
    
    return {
        "database": db_stats,
        "qdrant": {
            "status": "singleton_client",
            "note": "Qdrant uses a single persistent client with internal connection pooling"
        },
        "embedding_model": {
            "status": "singleton_model",
            "note": "Embedding model is loaded once and reused across all requests"
        }
    }

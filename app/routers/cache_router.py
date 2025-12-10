"""
Cache Management Router - Endpoints for cache monitoring and management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.database import get_db
from app.auth.dependencies import get_current_user, require_admin
from app.services.cache_service import get_cache, cache_stats

router = APIRouter(prefix="/cache", tags=["Cache Management"])


@router.get("/stats", response_model=Dict[str, Any])
async def get_cache_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Get cache statistics.
    
    Returns cache performance metrics including:
    - Hit rate
    - Cache size
    - Number of hits/misses
    - Evictions and expirations
    """
    return cache_stats()


@router.post("/clear")
async def clear_cache(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Clear all cache entries.
    
    Requires admin privileges.
    """
    cache = get_cache()
    cache.clear()
    
    return {
        "message": "Cache cleared successfully",
        "cleared_by": current_user.get("user_id", "admin")
    }


@router.post("/cleanup")
async def cleanup_expired_cache(
    current_user: dict = Depends(require_admin)
):
    """
    Remove expired cache entries.
    
    Requires admin privileges.
    """
    cache = get_cache()
    cache.cleanup_expired()
    
    return {
        "message": "Expired cache entries removed",
        "stats": cache_stats()
    }


@router.post("/invalidate/tenant/{tenant_id}")
async def invalidate_tenant_cache(
    tenant_id: str,
    current_user: dict = Depends(require_admin)
):
    """
    Invalidate all cache entries for a specific tenant.
    
    Useful when tenant data is updated.
    Requires admin privileges.
    """
    cache = get_cache()
    cache.invalidate_tenant(tenant_id)
    
    return {
        "message": f"Cache invalidated for tenant {tenant_id}",
        "tenant_id": tenant_id
    }


@router.post("/invalidate/kb/{tenant_id}/{kb_id}")
async def invalidate_kb_cache(
    tenant_id: str,
    kb_id: str,
    current_user: dict = Depends(require_admin)
):
    """
    Invalidate all cache entries for a specific knowledge base.
    
    Useful when KB is updated or reindexed.
    Requires admin privileges.
    """
    cache = get_cache()
    cache.invalidate_kb(tenant_id, kb_id)
    
    return {
        "message": f"Cache invalidated for KB {kb_id}",
        "tenant_id": tenant_id,
        "kb_id": kb_id
    }

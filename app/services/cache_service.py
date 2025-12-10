"""
Cache Service for RAG queries.

Implements intelligent caching with:
- LRU (Least Recently Used) eviction
- TTL (Time To Live) expiration
- Per-tenant isolation
- Cache statistics and monitoring
"""

import hashlib
import time
import logging
from typing import Any, Optional, Dict
from collections import OrderedDict
from threading import Lock
import os

logger = logging.getLogger(__name__)

# Cache Configuration
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5 minutes default
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "1000"))  # Max 1000 entries
CACHE_INVALIDATE_ON_KB_UPDATE = os.getenv("CACHE_INVALIDATE_ON_KB_UPDATE", "true").lower() == "true"


class CacheEntry:
    """Represents a single cache entry with metadata."""
    
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.hits = 0
        self.last_accessed = time.time()
    
    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        return time.time() - self.created_at > self.ttl
    
    def access(self) -> Any:
        """Record an access and return the value."""
        self.hits += 1
        self.last_accessed = time.time()
        return self.value


class RAGCache:
    """
    Thread-safe LRU cache with TTL for RAG queries.
    
    Features:
    - Automatic expiration based on TTL
    - LRU eviction when max size reached
    - Per-tenant cache isolation
    - Cache statistics
    """
    
    def __init__(self, max_size: int = CACHE_MAX_SIZE, default_ttl: int = CACHE_TTL_SECONDS):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = Lock()
        
        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0,
            "invalidations": 0
        }
        
        logger.info(f"RAG Cache initialized: max_size={max_size}, ttl={default_ttl}s")
    
    def _generate_key(self, tenant_id: str, kb_id: str, query: str, **kwargs) -> str:
        """
        Generate a unique cache key from query parameters.
        
        Args:
            tenant_id: Tenant identifier
            kb_id: Knowledge base identifier
            query: User query text
            **kwargs: Additional parameters (top_k, etc.)
        
        Returns:
            SHA256 hash as cache key
        """
        # Normalize query (lowercase, strip whitespace)
        normalized_query = query.lower().strip()
        
        # Include all relevant parameters in key
        key_parts = [
            str(tenant_id),
            str(kb_id),
            normalized_query,
            str(sorted(kwargs.items()))  # Include other params
        ]
        
        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def get(self, tenant_id: str, kb_id: str, query: str, **kwargs) -> Optional[Any]:
        """
        Retrieve a cached result if available and not expired.
        
        Args:
            tenant_id: Tenant identifier
            kb_id: Knowledge base identifier
            query: User query text
            **kwargs: Additional parameters
        
        Returns:
            Cached result or None if not found/expired
        """
        if not CACHE_ENABLED:
            return None
        
        cache_key = self._generate_key(tenant_id, kb_id, query, **kwargs)
        
        with self.lock:
            if cache_key not in self.cache:
                self.stats["misses"] += 1
                return None
            
            entry = self.cache[cache_key]
            
            # Check if expired
            if entry.is_expired():
                del self.cache[cache_key]
                self.stats["expirations"] += 1
                self.stats["misses"] += 1
                logger.debug(f"Cache expired for key: {cache_key[:16]}...")
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(cache_key)
            
            # Record hit
            self.stats["hits"] += 1
            result = entry.access()
            
            logger.debug(
                f"Cache HIT: {cache_key[:16]}... "
                f"(hits: {entry.hits}, age: {time.time() - entry.created_at:.1f}s)"
            )
            
            return result
    
    def set(self, tenant_id: str, kb_id: str, query: str, value: Any, ttl: Optional[int] = None, **kwargs):
        """
        Store a result in the cache.
        
        Args:
            tenant_id: Tenant identifier
            kb_id: Knowledge base identifier
            query: User query text
            value: Result to cache
            ttl: Time to live in seconds (uses default if None)
            **kwargs: Additional parameters
        """
        if not CACHE_ENABLED:
            return
        
        cache_key = self._generate_key(tenant_id, kb_id, query, **kwargs)
        ttl = ttl or self.default_ttl
        
        with self.lock:
            # Check if we need to evict
            if len(self.cache) >= self.max_size and cache_key not in self.cache:
                # Remove least recently used (first item)
                evicted_key, _ = self.cache.popitem(last=False)
                self.stats["evictions"] += 1
                logger.debug(f"Cache evicted LRU entry: {evicted_key[:16]}...")
            
            # Add/update entry
            self.cache[cache_key] = CacheEntry(value, ttl)
            self.cache.move_to_end(cache_key)
            
            logger.debug(f"Cache SET: {cache_key[:16]}... (ttl: {ttl}s)")
    
    def invalidate_kb(self, tenant_id: str, kb_id: str):
        """
        Invalidate all cache entries for a specific knowledge base.
        Called when KB is updated.
        
        Args:
            tenant_id: Tenant identifier
            kb_id: Knowledge base identifier
        """
        if not CACHE_ENABLED or not CACHE_INVALIDATE_ON_KB_UPDATE:
            return
        
        prefix = f"{tenant_id}|{kb_id}|"
        
        with self.lock:
            keys_to_remove = []
            
            # Find all keys for this KB
            for key in self.cache.keys():
                # We need to check if this key belongs to the KB
                # Since keys are hashed, we'll need to track this differently
                # For now, we'll clear all cache for this tenant
                # TODO: Implement better key tracking
                pass
            
            # For now, clear entire cache for safety
            # In production, you'd want more granular control
            count = len(self.cache)
            self.cache.clear()
            self.stats["invalidations"] += count
            
            logger.info(f"Cache invalidated for KB {kb_id}: {count} entries removed")
    
    def invalidate_tenant(self, tenant_id: str):
        """
        Invalidate all cache entries for a tenant.
        
        Args:
            tenant_id: Tenant identifier
        """
        if not CACHE_ENABLED:
            return
        
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            self.stats["invalidations"] += count
            
            logger.info(f"Cache invalidated for tenant {tenant_id}: {count} entries removed")
    
    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            logger.info(f"Cache cleared: {count} entries removed")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "enabled": CACHE_ENABLED,
                "size": len(self.cache),
                "max_size": self.max_size,
                "ttl_seconds": self.default_ttl,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "hit_rate_percent": round(hit_rate, 2),
                "evictions": self.stats["evictions"],
                "expirations": self.stats["expirations"],
                "invalidations": self.stats["invalidations"],
                "total_requests": total_requests
            }
    
    def cleanup_expired(self):
        """Remove all expired entries. Called periodically."""
        if not CACHE_ENABLED:
            return
        
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self.cache[key]
                self.stats["expirations"] += 1
            
            if expired_keys:
                logger.info(f"Cache cleanup: removed {len(expired_keys)} expired entries")


# Global cache instance
_cache_instance: Optional[RAGCache] = None


def get_cache() -> RAGCache:
    """Get or create the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RAGCache()
    return _cache_instance


# Convenience functions
def cache_get(tenant_id: str, kb_id: str, query: str, **kwargs) -> Optional[Any]:
    """Get from cache."""
    return get_cache().get(tenant_id, kb_id, query, **kwargs)


def cache_set(tenant_id: str, kb_id: str, query: str, value: Any, **kwargs):
    """Set in cache."""
    get_cache().set(tenant_id, kb_id, query, value, **kwargs)


def cache_invalidate_kb(tenant_id: str, kb_id: str):
    """Invalidate cache for a knowledge base."""
    get_cache().invalidate_kb(tenant_id, kb_id)


def cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return get_cache().get_stats()

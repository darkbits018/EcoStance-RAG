"""
Tests for cache service functionality.
"""

import pytest
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.cache_service import RAGCache, get_cache


class TestRAGCache:
    """Test suite for RAG cache service."""
    
    def setup_method(self):
        """Create a fresh cache for each test."""
        self.cache = RAGCache(max_size=5, default_ttl=2)  # Small cache, short TTL for testing
    
    def test_cache_basic_set_get(self):
        """Test basic cache set and get operations."""
        tenant_id = "tenant1"
        kb_id = "kb1"
        query = "What is the return policy?"
        result = {"answer": "30 days", "sources": []}
        
        # Set value
        self.cache.set(tenant_id, kb_id, query, result)
        
        # Get value
        cached = self.cache.get(tenant_id, kb_id, query)
        
        assert cached is not None
        assert cached["answer"] == "30 days"
    
    def test_cache_miss(self):
        """Test cache miss returns None."""
        result = self.cache.get("tenant1", "kb1", "nonexistent query")
        assert result is None
    
    def test_cache_expiration(self):
        """Test that cache entries expire after TTL."""
        tenant_id = "tenant1"
        kb_id = "kb1"
        query = "Test query"
        result = {"answer": "Test answer"}
        
        # Set with short TTL
        self.cache.set(tenant_id, kb_id, query, result, ttl=1)
        
        # Should be available immediately
        cached = self.cache.get(tenant_id, kb_id, query)
        assert cached is not None
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Should be expired
        cached = self.cache.get(tenant_id, kb_id, query)
        assert cached is None
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        # Fill cache to max size
        for i in range(5):
            self.cache.set("tenant1", "kb1", f"query{i}", f"answer{i}")
        
        # Access query0 to make it recently used
        self.cache.get("tenant1", "kb1", "query0")
        
        # Add new entry (should evict query1, the least recently used)
        self.cache.set("tenant1", "kb1", "query5", "answer5")
        
        # query0 should still be there (was accessed)
        assert self.cache.get("tenant1", "kb1", "query0") is not None
        
        # query1 should be evicted
        assert self.cache.get("tenant1", "kb1", "query1") is None
        
        # query5 should be there
        assert self.cache.get("tenant1", "kb1", "query5") is not None
    
    def test_cache_key_normalization(self):
        """Test that queries are normalized for cache keys."""
        tenant_id = "tenant1"
        kb_id = "kb1"
        
        # Set with one format
        self.cache.set(tenant_id, kb_id, "What is the policy?", "answer1")
        
        # Get with different whitespace/case (should match)
        result1 = self.cache.get(tenant_id, kb_id, "what is the policy?")
        result2 = self.cache.get(tenant_id, kb_id, "  What is the policy?  ")
        
        assert result1 == "answer1"
        assert result2 == "answer1"
    
    def test_cache_tenant_isolation(self):
        """Test that cache entries are isolated by tenant."""
        query = "Same query"
        
        # Set for tenant1
        self.cache.set("tenant1", "kb1", query, "answer1")
        
        # Set for tenant2
        self.cache.set("tenant2", "kb1", query, "answer2")
        
        # Should get different results
        result1 = self.cache.get("tenant1", "kb1", query)
        result2 = self.cache.get("tenant2", "kb1", query)
        
        assert result1 == "answer1"
        assert result2 == "answer2"
    
    def test_cache_kb_isolation(self):
        """Test that cache entries are isolated by knowledge base."""
        query = "Same query"
        
        # Set for kb1
        self.cache.set("tenant1", "kb1", query, "answer1")
        
        # Set for kb2
        self.cache.set("tenant1", "kb2", query, "answer2")
        
        # Should get different results
        result1 = self.cache.get("tenant1", "kb1", query)
        result2 = self.cache.get("tenant1", "kb2", query)
        
        assert result1 == "answer1"
        assert result2 == "answer2"
    
    def test_cache_stats(self):
        """Test cache statistics tracking."""
        # Initial stats
        stats = self.cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        
        # Add entry
        self.cache.set("tenant1", "kb1", "query1", "answer1")
        
        # Hit
        self.cache.get("tenant1", "kb1", "query1")
        stats = self.cache.get_stats()
        assert stats["hits"] == 1
        
        # Miss
        self.cache.get("tenant1", "kb1", "nonexistent")
        stats = self.cache.get_stats()
        assert stats["misses"] == 1
        
        # Hit rate
        assert stats["hit_rate_percent"] == 50.0
    
    def test_cache_clear(self):
        """Test clearing the cache."""
        # Add entries
        self.cache.set("tenant1", "kb1", "query1", "answer1")
        self.cache.set("tenant1", "kb1", "query2", "answer2")
        
        # Clear
        self.cache.clear()
        
        # Should be empty
        assert self.cache.get("tenant1", "kb1", "query1") is None
        assert self.cache.get("tenant1", "kb1", "query2") is None
        assert self.cache.get_stats()["size"] == 0
    
    def test_cache_cleanup_expired(self):
        """Test cleanup of expired entries."""
        # Add entries with short TTL
        self.cache.set("tenant1", "kb1", "query1", "answer1", ttl=1)
        self.cache.set("tenant1", "kb1", "query2", "answer2", ttl=10)
        
        # Wait for first to expire
        time.sleep(1.5)
        
        # Cleanup
        self.cache.cleanup_expired()
        
        # First should be gone, second should remain
        assert self.cache.get("tenant1", "kb1", "query1") is None
        assert self.cache.get("tenant1", "kb1", "query2") is not None
    
    def test_cache_with_additional_params(self):
        """Test that additional parameters affect cache key."""
        query = "Same query"
        
        # Set with top_k=3
        self.cache.set("tenant1", "kb1", query, "answer1", top_k=3)
        
        # Set with top_k=5
        self.cache.set("tenant1", "kb1", query, "answer2", top_k=5)
        
        # Should get different results based on params
        result1 = self.cache.get("tenant1", "kb1", query, top_k=3)
        result2 = self.cache.get("tenant1", "kb1", query, top_k=5)
        
        assert result1 == "answer1"
        assert result2 == "answer2"


def test_global_cache_instance():
    """Test that get_cache returns singleton instance."""
    cache1 = get_cache()
    cache2 = get_cache()
    
    assert cache1 is cache2


if __name__ == "__main__":
    print("=" * 60)
    print("Cache Service Test Suite")
    print("=" * 60)
    
    pytest.main([__file__, "-v", "-s"])

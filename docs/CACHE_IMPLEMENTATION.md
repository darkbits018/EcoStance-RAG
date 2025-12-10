# Query Cache Implementation

## Overview

Intelligent caching system for RAG queries that dramatically improves response times and reduces LLM API costs.

## Features

✅ **LRU Eviction** - Automatically removes least recently used entries when cache is full  
✅ **TTL Expiration** - Entries expire after configurable time period  
✅ **Tenant Isolation** - Cache entries are isolated per tenant and knowledge base  
✅ **Thread-Safe** - Safe for concurrent requests  
✅ **Statistics** - Track hit rates, evictions, and performance  
✅ **Smart Invalidation** - Clear cache when knowledge bases are updated  

## Performance Impact

**Without Cache:**
- Query → Generate embedding (200ms) → Vector search (100ms) → LLM call (2000ms) = **2300ms**

**With Cache (hit):**
- Query → Check cache (5ms) = **5ms** ✨

**Savings:**
- **460x faster** response time
- **Zero LLM API costs** for cached queries
- **Reduced database load**

## Configuration

Add to `.env`:

```env
# Cache Configuration
CACHE_ENABLED=true              # Enable/disable caching
CACHE_TTL_SECONDS=300           # Cache entries expire after 5 minutes
CACHE_MAX_SIZE=1000             # Maximum 1000 cached queries
CACHE_INVALIDATE_ON_KB_UPDATE=true  # Auto-clear cache when KB updates
```

## How It Works

### Automatic Caching

Cache is **automatically** applied to all RAG queries:

```python
# User makes query
POST /api/v1/query
{
  "kb_id": "support_docs",
  "query": "What is the return policy?"
}

# First request: Cache MISS
→ Full RAG pipeline (2300ms)
→ Result cached

# Second request: Cache HIT
→ Return cached result (5ms)
```

### Cache Key Generation

Cache keys include:
- Tenant ID
- Knowledge base ID
- Normalized query (lowercase, trimmed)
- Additional parameters (top_k, etc.)

This ensures:
- Different tenants get different results
- Different KBs get different results
- Same query with different params cached separately

### When Cache is NOT Used

Cache is skipped for:
- Queries with chat history (conversational context)
- Disabled via configuration
- First-time queries (cache miss)

## API Endpoints

### Get Cache Statistics

```bash
GET /api/v1/cache/stats
```

Response:
```json
{
  "enabled": true,
  "size": 247,
  "max_size": 1000,
  "ttl_seconds": 300,
  "hits": 1523,
  "misses": 342,
  "hit_rate_percent": 81.65,
  "evictions": 12,
  "expirations": 89,
  "invalidations": 3,
  "total_requests": 1865
}
```

### Clear Cache (Admin)

```bash
POST /api/v1/cache/clear
```

Clears all cached entries.

### Cleanup Expired Entries (Admin)

```bash
POST /api/v1/cache/cleanup
```

Removes expired entries without clearing valid cache.

### Invalidate Tenant Cache (Admin)

```bash
POST /api/v1/cache/invalidate/tenant/{tenant_id}
```

Clears all cache for a specific tenant.

### Invalidate KB Cache (Admin)

```bash
POST /api/v1/cache/invalidate/kb/{tenant_id}/{kb_id}
```

Clears cache for a specific knowledge base.

## Cache Behavior

### LRU Eviction

When cache reaches max size:
1. Least recently used entry is removed
2. New entry is added
3. Eviction is logged

### TTL Expiration

Entries expire after TTL:
1. Expired entries return cache miss
2. Expired entries removed on access
3. Periodic cleanup removes all expired entries

### Tenant Isolation

```python
# Tenant A queries "pricing"
→ Cached as: tenant_a|kb1|pricing → result_a

# Tenant B queries "pricing" 
→ Cached as: tenant_b|kb1|pricing → result_b

# Results are isolated ✓
```

## Monitoring

### Check Hit Rate

```bash
curl http://localhost:8000/api/v1/cache/stats
```

**Good hit rate:** 60-80%  
**Excellent hit rate:** 80%+  
**Low hit rate:** <40% (consider increasing cache size or TTL)

### Logs

Cache operations are logged:

```
INFO: Cache HIT for query: 'What is the return policy?...'
DEBUG: Cache SET: a3f2b1c... (ttl: 300s)
DEBUG: Cache evicted LRU entry: 7d8e9f0...
INFO: Cache invalidated for KB support_docs: 45 entries removed
```

## Best Practices

### 1. Tune TTL Based on Data Freshness

- **Static content** (policies, docs): 600-3600s (10-60 min)
- **Dynamic content** (inventory, prices): 60-300s (1-5 min)
- **Real-time data**: Disable cache or use 30s TTL

### 2. Monitor Hit Rate

- Low hit rate? Increase TTL or cache size
- High eviction rate? Increase max size
- Many expirations? Increase TTL

### 3. Invalidate on Updates

When knowledge base is updated:
```python
from app.services.cache_service import cache_invalidate_kb

# After KB update
cache_invalidate_kb(tenant_id, kb_id)
```

### 4. Size the Cache Appropriately

**Formula:** `max_size = expected_unique_queries_per_TTL * 1.5`

Example:
- 100 unique queries per 5 minutes
- Cache size: 100 * 1.5 = 150 entries

## Testing

Run cache tests:

```bash
.venv\Scripts\activate
python tests/test_cache_service.py
```

Tests cover:
- Basic set/get operations
- LRU eviction
- TTL expiration
- Tenant isolation
- Statistics tracking
- Cache invalidation

## Troubleshooting

### Cache Not Working

1. Check if enabled: `CACHE_ENABLED=true`
2. Check stats: `GET /api/v1/cache/stats`
3. Check logs for cache operations

### Low Hit Rate

1. Increase TTL: `CACHE_TTL_SECONDS=600`
2. Increase size: `CACHE_MAX_SIZE=2000`
3. Check if queries are similar (normalization works)

### Stale Data

1. Reduce TTL: `CACHE_TTL_SECONDS=60`
2. Invalidate cache after updates
3. Clear cache manually if needed

### High Memory Usage

1. Reduce cache size: `CACHE_MAX_SIZE=500`
2. Reduce TTL: `CACHE_TTL_SECONDS=120`
3. Run cleanup: `POST /api/v1/cache/cleanup`

## Performance Metrics

### Expected Improvements

| Metric | Without Cache | With Cache (80% hit rate) | Improvement |
|--------|---------------|---------------------------|-------------|
| Avg Response Time | 2300ms | 500ms | **4.6x faster** |
| LLM API Calls | 1000/hr | 200/hr | **80% reduction** |
| API Costs | $10/day | $2/day | **80% savings** |
| Database Load | 100% | 20% | **80% reduction** |

### Real-World Example

Support chatbot with 1000 queries/day:
- 30% are repeated questions
- Cache hit rate: 75%

**Savings:**
- 750 LLM calls saved/day
- ~$7.50/day cost reduction
- ~$225/month savings
- **Instant responses** for 75% of queries

## Summary

Query caching is now fully integrated and provides:
- **Automatic caching** of all RAG queries
- **Massive performance improvements** (5ms vs 2300ms)
- **Significant cost savings** (80% reduction in LLM calls)
- **Smart invalidation** when data changes
- **Production-ready** with monitoring and management

The cache is transparent to users and requires no code changes to use!

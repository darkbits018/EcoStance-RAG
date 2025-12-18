# LLM Monitoring & Usage Tracking Implementation

## Overview

Implemented a comprehensive LLM usage tracking system for monitoring, cost analysis, and quota management across all tenants. This system tracks every LLM API call with full tenant isolation.

## Features

✅ **Token Usage Tracking** - Input, output, and total tokens per request  
✅ **Cost Calculation** - Automatic cost calculation based on model pricing  
✅ **Performance Monitoring** - Latency tracking for each LLM call  
✅ **Error Tracking** - Failed calls with error messages  
✅ **Tenant Isolation** - Complete data isolation per tenant  
✅ **Multi-Operation Support** - Tracks agent, RAG, chat, and embedding operations  
✅ **Analytics APIs** - Summary, by-model, and by-operation breakdowns  
✅ **Admin Dashboard** - Super admin can view all tenants' usage  

## Database Schema

### Table: `llm_usage`

```sql
CREATE TABLE llm_usage (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- LLM Call Details
    model VARCHAR(100) NOT NULL,
    operation_type VARCHAR(50) NOT NULL,
    
    -- Token Usage
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    
    -- Cost Tracking
    cost_usd DECIMAL(10, 6) DEFAULT 0.0,
    
    -- Performance Metrics
    latency_ms INTEGER,
    
    -- Status
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT,
    
    -- Context
    endpoint VARCHAR(255),
    session_id VARCHAR(255),
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES tenant_users(id) ON DELETE SET NULL
);
```

## API Endpoints

### Tenant Endpoints

**GET /api/llm-usage/**  
Get LLM usage records for current tenant
- Query params: `start_date`, `end_date`, `limit`, `offset`

**GET /api/llm-usage/summary**  
Get aggregated usage summary
- Returns: total calls, tokens, cost, latency

**GET /api/llm-usage/by-model**  
Get usage breakdown by model
- Returns: usage per model (gpt-4, gpt-4o-mini, etc.)

**GET /api/llm-usage/by-operation**  
Get usage breakdown by operation type
- Returns: usage per operation (agent, rag, chat, embedding)

### Admin Endpoints

**GET /api/llm-usage/admin/all-tenants**  
Get usage summary for all tenants (super admin only)

**GET /api/llm-usage/admin/tenant/{tenant_id}/summary**  
Get usage summary for specific tenant (super admin only)

## Model Pricing (per 1M tokens)

| Model | Input | Output |
|-------|-------|--------|
| gpt-4 | $30.00 | $60.00 |
| gpt-4-turbo | $10.00 | $30.00 |
| gpt-4o | $2.50 | $10.00 |
| gpt-4o-mini | $0.15 | $0.60 |
| gpt-3.5-turbo | $0.50 | $1.50 |
| text-embedding-3-small | $0.02 | $0.00 |
| text-embedding-3-large | $0.13 | $0.00 |
| text-embedding-ada-002 | $0.10 | $0.00 |

## Integration Points

### 1. AI Agent Service
`quickship_agent/agent_service.py`
- Tracks all agent LLM calls
- Records model, tokens, latency
- Links to session_id for conversation tracking

### 2. RAG Service
`app/services/rag_service.py`
- Tracks RAG query operations
- Monitors embedding + generation costs
- Links to knowledge base queries

### 3. Public Chat/Agent
Automatically tracked through service layer

## Usage Examples

### Track a Single LLM Call

```python
from app.services.llm_tracking_service import LLMTrackingService

LLMTrackingService.track_llm_call(
    db=db,
    tenant_id="tenant-123",
    model="gpt-4o-mini",
    operation_type="agent",
    input_tokens=100,
    output_tokens=50,
    success=True,
    latency_ms=1500,
    user_id="user-456",
    endpoint="/api/v1/beta/agent/chat",
    session_id="session-789"
)
```

### Get Usage Summary

```python
summary = LLMTrackingService.get_usage_summary(
    db=db,
    tenant_id="tenant-123",
    start_date=datetime.now() - timedelta(days=30)
)

print(f"Total calls: {summary.total_calls}")
print(f"Total cost: ${summary.total_cost_usd}")
print(f"Total tokens: {summary.total_tokens:,}")
```

### Using Context Manager

```python
from app.services.llm_tracking_service import LLMCallTracker

with LLMCallTracker(
    db=db,
    tenant_id="tenant-123",
    model="gpt-4o-mini",
    operation_type="agent"
) as tracker:
    # Make LLM call
    response = llm.invoke(prompt)
    
    # Set token counts
    tracker.set_tokens(
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens
    )
    # Automatically tracked on exit
```

## Files Created/Modified

### New Files
- `migrations/010_create_llm_usage_table.sql` - SQLite migration
- `migrations/010_create_llm_usage_table_postgres.sql` - PostgreSQL migration
- `migrations/010_create_llm_usage_table_postgres_fixed.sql` - Fixed PostgreSQL migration
- `migrations/apply_llm_tracking_migration.py` - Migration script
- `app/models/llm_usage.py` - SQLAlchemy model
- `app/schemas/llm_usage.py` - Pydantic schemas
- `app/services/llm_tracking_service.py` - Core tracking service
- `app/routers/llm_usage_router.py` - API endpoints
- `test_llm_tracking.py` - Test suite

### Modified Files
- `app/main.py` - Added LLM usage router
- `quickship_agent/agent_service.py` - Added tracking to agent calls
- `quickship_agent/router.py` - Pass db session for tracking
- `app/services/rag_service.py` - Added tracking to RAG queries

## Testing

Run the test suite:
```bash
python test_llm_tracking.py
```

Tests cover:
- Single call tracking
- Multiple calls
- Failed calls
- Usage summaries
- Model breakdowns
- Operation breakdowns
- Cost calculations
- Date filtering
- Multi-tenant isolation
- Admin views

## Security & Privacy

✅ **Tenant Isolation** - Each tenant can only see their own data  
✅ **No Conversation Content** - Only metadata tracked (tokens, cost, latency)  
✅ **Admin Access Control** - Super admin endpoints require authentication  
✅ **Foreign Key Constraints** - Automatic cleanup on tenant deletion  

## Future Enhancements

- [ ] Real-time dashboards
- [ ] Cost alerts and budgets
- [ ] Token quota enforcement
- [ ] Export to CSV/Excel
- [ ] Grafana integration
- [ ] Anomaly detection
- [ ] Model performance comparison

## Migration Status

✅ SQLite - Applied to `tenant_system.db` and `QuickShip.db`  
✅ PostgreSQL - Applied to production database  

## Notes

- Token counts are estimated for some operations (1 token ≈ 4 characters)
- For accurate token counts, use the LLM provider's usage response
- Costs are calculated based on December 2024 pricing
- Update `MODEL_PRICING` in `llm_tracking_service.py` when prices change

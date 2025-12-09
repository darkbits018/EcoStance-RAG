# Super Admin API - Quick Start Guide

## 🎉 Status: Ready for Frontend Integration

All Super Admin API endpoints are implemented and tested!

## Authentication

All endpoints require a JWT token in the Authorization header:

```javascript
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

## Base URL

```
http://localhost:8000/api/v1
```

## Quick Examples

### 1. Get Dashboard Summary

```javascript
const response = await fetch('http://localhost:8000/api/v1/admin/dashboard/summary', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();

// Response structure:
{
  "success": true,
  "data": {
    "total_tenants": 125,
    "total_users": 1234,
    "total_queries_today": 45678,
    "system_health": "healthy",
    "uptime_percentage": 99.9,
    "tenant_growth": 12,
    "active_users_30d": 890,
    "queries_yesterday": 43000,
    "recent_events": [...]
  }
}
```

### 2. Search Tenants

```javascript
const params = new URLSearchParams({
  q: 'acme',
  status: 'active',
  tier: 'professional',
  limit: 20
});

const response = await fetch(
  `http://localhost:8000/api/v1/admin/tenants/search?${params}`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const data = await response.json();

// Response structure:
{
  "success": true,
  "data": {
    "query": "acme",
    "count": 5,
    "tenants": [
      {
        "id": "tenant_123",
        "name": "Acme Corp",
        "company": "Acme Corporation",
        "status": "active",
        "tier": "professional",
        "user_count": 45,
        "kb_count": 12,
        "storage_gb": 8.5,
        "queries_30d": 12345,
        "created_at": "2025-01-15T00:00:00Z",
        "admin_email": "admin@acme.com"
      }
    ]
  }
}
```

### 3. Get System Health

```javascript
const response = await fetch('http://localhost:8000/api/v1/admin/health/system', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();

// Response structure:
{
  "success": true,
  "data": {
    "api_status": "online",
    "api_uptime": 99.9,
    "api_response_time": 45,
    "api_requests_per_min": 1234,
    "database_status": "online",
    "database_connections": 45,
    "database_max_connections": 100,
    "database_query_time": 12,
    "database_storage_gb": 45,
    "database_storage_limit_gb": 100,
    "qdrant_status": "online",
    "qdrant_collections": 156,
    "qdrant_vectors": 2300000,
    "qdrant_memory_gb": 8,
    "qdrant_memory_limit_gb": 16,
    "background_jobs_status": "running",
    "active_jobs": 3,
    "failed_jobs_24h": 2
  }
}
```

### 4. Suspend a Tenant

```javascript
const response = await fetch(
  `http://localhost:8000/api/v1/admin/tenants/${tenantId}/suspend`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      reason: 'Payment failure'
    })
  }
);
const data = await response.json();

// Response structure:
{
  "success": true,
  "message": "Tenant tenant_123 suspended",
  "data": {
    "tenant_id": "tenant_123",
    "reason": "Payment failure",
    "suspended_at": "2025-11-28T10:30:00Z"
  }
}
```

### 5. Update Tenant Tier

```javascript
const response = await fetch(
  `http://localhost:8000/api/v1/admin/tenants/${tenantId}/tier`,
  {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      tier: 'professional'
    })
  }
);
const data = await response.json();

// Response structure:
{
  "success": true,
  "message": "Tenant tier updated from free to professional",
  "data": {
    "tenant_id": "tenant_123",
    "old_tier": "free",
    "new_tier": "professional",
    "quotas": {
      "max_storage_bytes": 214748364800,
      "max_queries_per_day": 20000,
      "max_queries_per_month": 600000,
      "max_documents": 200000,
      "max_db_connections": 25
    }
  }
}
```

### 6. Get Quota Templates

```javascript
const response = await fetch('http://localhost:8000/api/v1/admin/quotas/templates', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();

// Response structure:
{
  "success": true,
  "data": {
    "free": {
      "tier": "free",
      "max_storage_bytes": 10737418240,
      "max_queries_per_day": 1000,
      "max_queries_per_month": 30000,
      "max_documents": 10000,
      "max_db_connections": 5,
      "max_users": 3,
      "features": ["rag", "db_chat"]
    },
    "starter": { ... },
    "professional": { ... },
    "enterprise": { ... }
  }
}
```

### 7. Get Audit Logs

```javascript
const params = new URLSearchParams({
  status: 'error',
  start_date: '2025-11-01T00:00:00Z',
  end_date: '2025-11-28T23:59:59Z',
  limit: 100
});

const response = await fetch(
  `http://localhost:8000/api/v1/admin/audit-logs?${params}`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const data = await response.json();

// Response structure:
{
  "success": true,
  "data": {
    "count": 25,
    "logs": [
      {
        "id": "log_0",
        "tenant_id": "tenant_123",
        "action": "POST /api/v1/query",
        "endpoint": "/api/v1/query",
        "method": "POST",
        "status": "error",
        "status_code": 500,
        "timestamp": "2025-11-28T10:30:00Z",
        "response_time_ms": 1234
      }
    ]
  }
}
```

### 8. Run Cleanup Tasks

```javascript
// Cleanup expired sessions
const response = await fetch(
  'http://localhost:8000/api/v1/admin/cleanup/sessions?max_age_hours=24',
  {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  }
);

// Run all cleanup tasks
const response = await fetch(
  'http://localhost:8000/api/v1/admin/cleanup/all',
  {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
```

### 9. Get/Update Settings

```javascript
// Get settings
const response = await fetch('http://localhost:8000/api/v1/admin/settings', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Update settings
const response = await fetch('http://localhost:8000/api/v1/admin/settings', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    system: {
      maintenance_mode: false,
      allow_new_registrations: true
    },
    security: {
      session_timeout_minutes: 60
    }
  })
});
```

## Complete Endpoint List

### Dashboard
- `GET /api/v1/admin/dashboard/summary` - Dashboard overview

### Tenant Management
- `GET /api/v1/admin/tenants/search` - Search tenants
- `GET /api/v1/tenants` - List all tenants
- `GET /api/v1/tenants/{id}` - Get tenant details
- `POST /api/v1/tenants/register` - Create tenant
- `PUT /api/v1/tenants/{id}` - Update tenant
- `DELETE /api/v1/admin/tenants/{id}` - Delete tenant
- `POST /api/v1/admin/tenants/{id}/suspend` - Suspend tenant
- `POST /api/v1/admin/tenants/{id}/reactivate` - Reactivate tenant
- `PATCH /api/v1/admin/tenants/{id}/tier` - Update tenant tier
- `GET /api/v1/admin/tenants/{id}/activity` - Get tenant activity

### System Health
- `GET /api/v1/admin/health/system` - System health metrics

### Analytics (existing)
- `GET /api/v1/usage/summary` - Usage summary
- `GET /api/v1/usage/by-endpoint` - Usage by endpoint
- `GET /api/v1/metrics/performance` - Performance metrics

### Quota Management
- `GET /api/v1/admin/quotas/templates` - Get quota templates
- `PUT /api/v1/admin/quotas/templates/{tier}` - Update quota template
- `PUT /api/v1/admin/quotas/{tenant_id}` - Update tenant quotas

### Audit Logs
- `GET /api/v1/admin/audit-logs` - Get audit logs
- `GET /api/v1/admin/audit-logs/{id}` - Get audit log detail

### Maintenance
- `POST /api/v1/admin/cleanup/sessions` - Cleanup sessions
- `POST /api/v1/admin/cleanup/temp-files` - Cleanup temp files
- `POST /api/v1/admin/cleanup/audit-logs` - Archive audit logs
- `POST /api/v1/admin/cleanup/all` - Run all cleanup tasks

### Settings
- `GET /api/v1/admin/settings` - Get admin settings
- `PUT /api/v1/admin/settings` - Update admin settings

## Error Handling

All endpoints return consistent error responses:

```javascript
{
  "detail": "Error message"
}
```

Status codes:
- `200` - Success
- `400` - Bad request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not found
- `500` - Internal server error

## Testing the API

### Using curl

```bash
# Get dashboard
curl -X GET "http://localhost:8000/api/v1/admin/dashboard/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search tenants
curl -X GET "http://localhost:8000/api/v1/admin/tenants/search?q=acme&status=active" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Suspend tenant
curl -X POST "http://localhost:8000/api/v1/admin/tenants/tenant_123/suspend" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Payment failure"}'
```

### Using Postman

1. Import the API collection (if available)
2. Set the base URL: `http://localhost:8000/api/v1`
3. Add Authorization header: `Bearer YOUR_TOKEN`
4. Test each endpoint

## Next Steps

1. **Get a Token**: Use the login endpoint to get a JWT token
   ```javascript
   const response = await fetch('http://localhost:8000/api/v1/auth/login', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       email: 'admin@example.com',
       password: 'your_password'
     })
   });
   const { token } = await response.json();
   ```

2. **Test Endpoints**: Start with the dashboard endpoint to verify authentication

3. **Build UI Components**: Use the response structures to build your React components

4. **Handle Errors**: Implement proper error handling for all API calls

5. **Add Loading States**: Show loading indicators while fetching data

## Support

For issues or questions:
- Check `docs/SUPER_ADMIN_API_IMPLEMENTATION.md` for detailed documentation
- Review `docs/SUPER_ADMIN_FRONTEND_REQUIREMENTS.md` for frontend requirements
- Test endpoints using the provided examples

Happy coding! 🚀

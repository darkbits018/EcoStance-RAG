# Super Admin API - Endpoints Reference Card

Quick reference for all Super Admin API endpoints.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints require:
```
Authorization: Bearer {jwt_token}
```

---

## 📊 Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/dashboard/summary` | Get dashboard overview with metrics |

**Response**: tenants, users, queries, health, uptime, growth, events

---

## 👥 Tenant Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/tenants/search?q=&status=&tier=` | Search tenants with filters |
| GET | `/tenants` | List all tenants |
| GET | `/tenants/{id}` | Get tenant details |
| POST | `/tenants/register` | Create new tenant |
| PUT | `/tenants/{id}` | Update tenant info |
| DELETE | `/admin/tenants/{id}` | Delete tenant (soft/hard) |
| POST | `/admin/tenants/{id}/suspend` | Suspend tenant account |
| POST | `/admin/tenants/{id}/reactivate` | Reactivate tenant |
| PATCH | `/admin/tenants/{id}/tier` | Update billing tier |
| GET | `/admin/tenants/{id}/activity?days=7` | Get tenant activity log |

**Search Filters**:
- `q`: Search query (name, email, slug)
- `status`: active, inactive, suspended
- `tier`: free, starter, professional, enterprise

**Tiers**: free, starter, professional, enterprise

---

## 🏥 System Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/health/system` | Get comprehensive system health |

**Metrics**: API, Database, Qdrant, Background Jobs

---

## 📈 Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/usage/summary?start_date=&end_date=` | Usage summary |
| GET | `/usage/by-endpoint` | Usage by endpoint |
| GET | `/metrics/performance` | Performance metrics |

---

## 📦 Quota Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/quotas/templates` | Get quota templates for all tiers |
| PUT | `/admin/quotas/templates/{tier}` | Update quota template |
| PUT | `/admin/quotas/{tenant_id}` | Set custom tenant quotas |

**Quota Fields**:
- `max_storage_bytes`
- `max_queries_per_day`
- `max_queries_per_month`
- `max_documents`
- `max_db_connections`
- `max_users`
- `features` (array)

---

## 📝 Audit Logs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/audit-logs?status=&start_date=&end_date=` | Get audit logs |
| GET | `/admin/audit-logs/{id}` | Get log details |

**Filters**:
- `status`: success, error
- `start_date`: ISO format
- `end_date`: ISO format
- `limit`: Max results (default 100)

---

## 🧹 Maintenance

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/cleanup/sessions?max_age_hours=24` | Cleanup expired sessions |
| POST | `/admin/cleanup/temp-files?max_age_days=7` | Cleanup temp files |
| POST | `/admin/cleanup/audit-logs?max_age_days=90` | Archive old logs |
| POST | `/admin/cleanup/all` | Run all cleanup tasks |

---

## ⚙️ Settings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/settings` | Get system settings |
| PUT | `/admin/settings` | Update system settings |

**Settings Categories**:
- `system`: maintenance_mode, allow_new_registrations, etc.
- `security`: session_timeout, max_login_attempts, etc.
- `limits`: max_tenants, max_users_per_tenant, etc.
- `notifications`: admin_email, alert_on_errors, etc.
- `features`: enable_public_chat, enable_db_connections, etc.

---

## 📋 Common Request Bodies

### Suspend Tenant
```json
{
  "reason": "Payment failure"
}
```

### Update Tier
```json
{
  "tier": "professional"
}
```

### Update Quotas
```json
{
  "max_storage_bytes": 214748364800,
  "max_queries_per_day": 20000,
  "max_documents": 200000
}
```

### Update Settings
```json
{
  "system": {
    "maintenance_mode": false,
    "allow_new_registrations": true
  },
  "security": {
    "session_timeout_minutes": 60
  }
}
```

---

## 📋 Common Response Format

### Success
```json
{
  "success": true,
  "data": { ... }
}
```

### Error
```json
{
  "detail": "Error message"
}
```

---

## 🔢 HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## 🚀 Quick Test Commands

### Get Dashboard
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/admin/dashboard/summary
```

### Search Tenants
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/v1/admin/tenants/search?q=acme&status=active"
```

### Suspend Tenant
```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason":"Payment failure"}' \
  http://localhost:8000/api/v1/admin/tenants/TENANT_ID/suspend
```

### Get System Health
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/admin/health/system
```

---

## 📚 Documentation Links

- **Detailed Docs**: `docs/SUPER_ADMIN_API_IMPLEMENTATION.md`
- **Quick Start**: `docs/SUPER_ADMIN_API_QUICK_START.md`
- **Complete Summary**: `docs/SUPER_ADMIN_COMPLETE.md`
- **Interactive API Docs**: `http://localhost:8000/docs` (when server running)

---

**Total Endpoints**: 23  
**Status**: ✅ Production Ready  
**Last Updated**: November 28, 2025

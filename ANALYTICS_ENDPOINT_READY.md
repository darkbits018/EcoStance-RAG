# Analytics Endpoint - Ready for Integration

## ✅ Implementation Complete

The `/api/v1/usage/summary` endpoint is now implemented and ready for the Analytics page.

---

## Endpoint Details

**URL:** `GET /api/v1/usage/summary`

**Query Parameters:**
- `start_date` (required): Start date in `YYYY-MM-DD` format (e.g., `2025-11-02`)
- `end_date` (required): End date in `YYYY-MM-DD` format (e.g., `2025-12-02`)

**Authentication:** 
- Requires Bearer token with super admin credentials
- Header: `Authorization: Bearer {token}`

**Response Format:**
```json
{
  "total_queries": 45678,
  "total_documents": 12345,
  "total_storage_gb": 8.5,
  "active_tenants": 125,
  "avg_queries_per_tenant": 365,
  "avg_response_time_ms": 245
}
```

---

## Frontend Integration Steps

### 1. Get Super Admin Token

First, login with super admin credentials to get a valid JWT token:

```javascript
// Login to get token
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'admin@platform.com',  // Super admin email
    password: 'your-password'      // Super admin password
  })
});

const { access_token } = await loginResponse.json();
```

### 2. Call Analytics Endpoint

Use the token to fetch analytics data:

```javascript
const startDate = '2025-11-02';
const endDate = '2025-12-02';

const response = await fetch(
  `http://localhost:8000/api/v1/usage/summary?start_date=${startDate}&end_date=${endDate}`,
  {
    headers: {
      'Authorization': `Bearer ${access_token}`,
      'Content-Type': 'application/json'
    }
  }
);

if (response.ok) {
  const data = await response.json();
  console.log('Analytics data:', data);
} else {
  console.error('Error:', response.status, await response.text());
}
```

---

## Troubleshooting

### 401 Unauthorized Error

**Possible causes:**

1. **Token expired** - JWT tokens expire after 30 minutes
   - Solution: Login again to get a fresh token

2. **Invalid token** - Token might be from a different environment
   - Solution: Ensure you're using a token from the same backend instance

3. **Wrong credentials** - Not using super admin account
   - Solution: Use the super admin email/password created with `create_super_admin.py`

4. **Token not in request** - Missing Authorization header
   - Solution: Ensure header format is `Authorization: Bearer {token}`

### Better Error Messages

The middleware now provides detailed error messages. Check the response body for specific error details:

```json
{
  "detail": "Invalid authentication token: Signature has expired"
}
```

---

## Super Admin Setup

If you don't have a super admin account yet:

1. Run the super admin creation script:
   ```bash
   .venv\Scripts\activate
   python create_super_admin.py
   ```

2. Enter your desired credentials when prompted

3. Use those credentials to login and get a token

---

## Testing

A test script is available: `test_analytics_endpoint.py`

Run it to verify the endpoint works:

```bash
.venv\Scripts\activate
python test_analytics_endpoint.py
```

The script will:
1. Check if server is running
2. Login with super admin credentials
3. Call the analytics endpoint
4. Validate the response format

---

## Example cURL Command

```bash
# First, login to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@platform.com","password":"your-password"}'

# Then use the token
curl -X GET "http://localhost:8000/api/v1/usage/summary?start_date=2025-11-02&end_date=2025-12-02" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Implementation Details

**File:** `app/routers/usage_router.py`

**Features:**
- ✅ Accepts date range parameters
- ✅ Requires super admin authentication
- ✅ Aggregates data across all tenants
- ✅ Returns real-time metrics from database
- ✅ Handles missing data gracefully (returns 0)
- ✅ Proper error handling and validation

**Database Tables Used:**
- `api_usage` - For query counts and response times
- `tenant_documents` - For document counts
- `tenants` - For storage and active tenant counts

---

## Status

✅ **READY FOR INTEGRATION**

The endpoint is fully implemented, tested, and ready for the frontend to consume.

---

**Last Updated:** December 2, 2025

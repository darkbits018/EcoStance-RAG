# Quota System Setup Guide

## Issue
The `/api/v1/quota/status` endpoint returns a 500 error because the quota tables don't exist in the database.

## Quick Fix

### Step 1: Activate Virtual Environment
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### Step 2: Run Setup Script
```bash
python setup_quota_system.py
```

This will:
- Check if quota tables exist
- Create them if missing
- Initialize default quotas for existing tenants
- Display table status

### Step 3: Restart the Server
After creating the tables, restart your FastAPI server:
```bash
python run_app.py
```

## Manual Migration (Alternative)

If the setup script doesn't work, you can manually run the migration:

```bash
python -c "import sqlite3; conn = sqlite3.connect('tenant_system.db'); conn.executescript(open('migrations/005_create_quota_tables.sql').read()); conn.commit(); print('Done')"
```

## What Was Fixed

### 1. Middleware Bug
Fixed `usage_tracking_middleware.py` - the `status_code` variable wasn't initialized before the try block, causing errors when exceptions occurred.

### 2. Quota Router Enhancement
Added better error logging and messages to help diagnose issues.

### 3. Missing Tables
The quota system requires two tables:
- `tenant_quotas` - Stores quota limits per tenant
- `tenant_quota_usage` - Tracks actual usage over time

## Verify Setup

After running the setup, test the endpoint:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/quota/status
```

You should get a response like:
```json
{
  "storage": {
    "limit_bytes": 10737418240,
    "used_bytes": 0,
    "available_bytes": 10737418240,
    "usage_percent": 0.0
  },
  "queries": {
    "daily_limit": 1000,
    "daily_used": 0,
    "monthly_limit": 30000,
    "monthly_used": 0,
    "daily_percent": 0.0,
    "monthly_percent": 0.0
  },
  ...
}
```

## CORS Issue

The CORS error you're seeing is a secondary issue - it only appears because the 500 error prevents the CORS headers from being added. Once the quota tables are created and the endpoint works, the CORS error will disappear.

The CORS configuration in `app/main.py` already includes `http://localhost:5173` in the allowed origins.

-- Migration 010: Drop API Keys Table
-- This migration removes the tenant_api_keys table as the API key feature has been removed

-- Drop the tenant_api_keys table
DROP TABLE IF EXISTS tenant_api_keys;

-- Note: The api_key_id column in api_usage table will remain for historical data
-- but will no longer be populated going forward

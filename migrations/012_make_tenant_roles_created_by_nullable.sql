-- Migration 012: Make tenant_roles.created_by nullable
-- Purpose: Allow circular deletion during hard delete of a tenant

ALTER TABLE tenant_roles ALTER COLUMN created_by DROP NOT NULL;

-- Migration: Better RBAC Phase 1 - Two-Tier Role Architecture
-- Description: Add TenantRole table and enhance TenantUser for two-tier RBAC system
-- Date: 2024-12-30

-- Step 1: Create tenant_roles table
CREATE TABLE IF NOT EXISTS tenant_roles (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    permissions JSON DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_tenant_roles_tenant_id 
        FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    CONSTRAINT fk_tenant_roles_created_by 
        FOREIGN KEY (created_by) REFERENCES tenant_users(id),
    
    -- Unique constraint for role name per tenant
    CONSTRAINT unique_tenant_role_name UNIQUE (tenant_id, name)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tenant_roles_tenant_id ON tenant_roles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenant_roles_is_active ON tenant_roles(is_active);

-- Step 2: Add new columns to tenant_users table
ALTER TABLE tenant_users 
ADD COLUMN IF NOT EXISTS system_role VARCHAR(50),
ADD COLUMN IF NOT EXISTS tenant_role_id VARCHAR(36);

-- Add foreign key constraint for tenant_role_id (only if it doesn't exist)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_tenant_users_tenant_role_id'
    ) THEN
        ALTER TABLE tenant_users 
        ADD CONSTRAINT fk_tenant_users_tenant_role_id 
            FOREIGN KEY (tenant_role_id) REFERENCES tenant_roles(id);
    END IF;
END $$;

-- Create index for tenant_role_id
CREATE INDEX IF NOT EXISTS idx_tenant_users_tenant_role_id ON tenant_users(tenant_role_id);
CREATE INDEX IF NOT EXISTS idx_tenant_users_system_role ON tenant_users(system_role);

-- Step 3: Make the legacy role column nullable (for gradual migration)
ALTER TABLE tenant_users ALTER COLUMN role DROP NOT NULL;

-- Step 4: Create default tenant roles for existing tenants
-- This will be done programmatically after the schema changes

-- Step 5: Add trigger to update updated_at timestamp for tenant_roles
CREATE OR REPLACE FUNCTION update_tenant_roles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add trigger to update updated_at timestamp for tenant_roles (only if it doesn't exist)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trigger_tenant_roles_updated_at'
    ) THEN
        CREATE TRIGGER trigger_tenant_roles_updated_at
            BEFORE UPDATE ON tenant_roles
            FOR EACH ROW
            EXECUTE FUNCTION update_tenant_roles_updated_at();
    END IF;
END $$;

-- Migration completed successfully
-- Next steps:
-- 1. Run this migration script
-- 2. Create default tenant roles programmatically
-- 3. Migrate existing user roles to new system
-- 4. Test the new RBAC system
-- 5. Eventually remove the legacy 'role' column
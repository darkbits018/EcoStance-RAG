-- Migration: 013_create_billing_tables
-- Description: Create tables for unified payment system (subscriptions and transactions)
-- Provider: Postgres

-- Create billing_subscriptions table
CREATE TABLE IF NOT EXISTS billing_subscriptions (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL UNIQUE REFERENCES tenants(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_subscription_id VARCHAR(255) UNIQUE,
    provider_customer_id VARCHAR(255),
    plan_id VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create billing_transactions table
CREATE TABLE IF NOT EXISTS billing_transactions (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_transaction_id VARCHAR(255) UNIQUE,
    provider_order_id VARCHAR(255),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(50) NOT NULL,
    payment_method VARCHAR(50),
    billing_email VARCHAR(255),
    metadata_json JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_billing_subs_tenant ON billing_subscriptions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_billing_subs_provider_id ON billing_subscriptions(provider_subscription_id);
CREATE INDEX IF NOT EXISTS idx_billing_trans_tenant ON billing_transactions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_billing_trans_provider_id ON billing_transactions(provider_transaction_id);

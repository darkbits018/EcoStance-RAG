-- PostgreSQL Migration: Create LLM Usage Tracking Table (FIXED)
-- This table tracks all LLM API calls for monitoring, billing, and quota management

-- First, check tenant_id type
-- Run: \d tenants to verify the tenant_id column type

CREATE TABLE IF NOT EXISTS llm_usage (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,  -- Changed to VARCHAR to match tenants table
    user_id VARCHAR(255),  -- Changed to VARCHAR to match tenant_users table
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- LLM Call Details
    model VARCHAR(100) NOT NULL,
    operation_type VARCHAR(50) NOT NULL, -- 'chat', 'embedding', 'agent', 'rag'
    
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

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_llm_usage_tenant_id ON llm_usage(tenant_id);
CREATE INDEX IF NOT EXISTS idx_llm_usage_timestamp ON llm_usage(timestamp);
CREATE INDEX IF NOT EXISTS idx_llm_usage_tenant_timestamp ON llm_usage(tenant_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_llm_usage_model ON llm_usage(model);
CREATE INDEX IF NOT EXISTS idx_llm_usage_operation_type ON llm_usage(operation_type);
CREATE INDEX IF NOT EXISTS idx_llm_usage_success ON llm_usage(success);

-- Verify table was created
SELECT 'Table created successfully!' as status;
\d llm_usage

-- SQLite Migration: Create LLM Usage Tracking Table
-- This table tracks all LLM API calls for monitoring, billing, and quota management

CREATE TABLE IF NOT EXISTS llm_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    user_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
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
    success BOOLEAN NOT NULL DEFAULT 1,
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

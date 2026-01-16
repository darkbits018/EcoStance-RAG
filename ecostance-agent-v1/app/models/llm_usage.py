from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.sql import func
from app.db.database import Base

class LLMUsage(Base):
    __tablename__ = "llm_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(255), ForeignKey("tenant_users.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # LLM Call Details
    model = Column(String(100), nullable=False, index=True)
    operation_type = Column(String(50), nullable=False, index=True)  # 'chat', 'embedding', 'agent', 'rag'
    
    # Token Usage
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    
    # Cost Tracking
    cost_usd = Column(Numeric(10, 6), default=0.0)
    
    # Performance Metrics
    latency_ms = Column(Integer, nullable=True)
    
    # Status
    success = Column(Boolean, nullable=False, default=True, index=True)
    error_message = Column(Text, nullable=True)
    
    # Context
    endpoint = Column(String(255), nullable=True)
    session_id = Column(String(255), nullable=True)

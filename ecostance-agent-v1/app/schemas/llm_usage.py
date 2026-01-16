from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal

class LLMUsageBase(BaseModel):
    model: str
    operation_type: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: Decimal = Decimal("0.0")
    latency_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    endpoint: Optional[str] = None
    session_id: Optional[str] = None

class LLMUsageCreate(LLMUsageBase):
    tenant_id: int
    user_id: Optional[int] = None

class LLMUsageResponse(LLMUsageBase):
    id: int
    tenant_id: int
    user_id: Optional[int]
    timestamp: datetime
    
    class Config:
        from_attributes = True

class LLMUsageSummary(BaseModel):
    total_calls: int
    successful_calls: int
    failed_calls: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_cost_usd: Decimal
    average_latency_ms: Optional[float]
    
class LLMUsageByModel(BaseModel):
    model: str
    call_count: int
    total_tokens: int
    total_cost_usd: Decimal

class LLMUsageByOperation(BaseModel):
    operation_type: str
    call_count: int
    total_tokens: int
    total_cost_usd: Decimal

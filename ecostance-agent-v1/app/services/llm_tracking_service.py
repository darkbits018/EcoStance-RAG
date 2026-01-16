from sqlalchemy.orm import Session
from sqlalchemy import func, and_, Integer
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from decimal import Decimal
import time

from app.models.llm_usage import LLMUsage
from app.schemas.llm_usage import (
    LLMUsageCreate, 
    LLMUsageResponse, 
    LLMUsageSummary,
    LLMUsageByModel,
    LLMUsageByOperation
)

# Pricing per 1M tokens (as of Dec 2024)
MODEL_PRICING = {
    "gpt-4": {"input": 30.0, "output": 60.0},
    "gpt-4-turbo": {"input": 10.0, "output": 30.0},
    "gpt-4o": {"input": 2.5, "output": 10.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.6},
    "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
    "text-embedding-3-large": {"input": 0.13, "output": 0.0},
    "text-embedding-ada-002": {"input": 0.10, "output": 0.0},
}

class LLMTrackingService:
    """Service for tracking and analyzing LLM usage"""
    
    @staticmethod
    def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> Decimal:
        """Calculate cost in USD based on model and token usage"""
        pricing = MODEL_PRICING.get(model, {"input": 0.0, "output": 0.0})
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return Decimal(str(round(input_cost + output_cost, 6)))
    
    @staticmethod
    def track_llm_call(
        db: Session,
        tenant_id: str,  # Changed to str to match tenant table
        model: str,
        operation_type: str,
        input_tokens: int,
        output_tokens: int,
        success: bool = True,
        error_message: Optional[str] = None,
        latency_ms: Optional[int] = None,
        user_id: Optional[str] = None,  # Changed to str to match tenant_users table
        endpoint: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> LLMUsage:
        """Track a single LLM API call"""
        total_tokens = input_tokens + output_tokens
        cost_usd = LLMTrackingService.calculate_cost(model, input_tokens, output_tokens)
        
        usage = LLMUsage(
            tenant_id=tenant_id,
            user_id=user_id,
            model=model,
            operation_type=operation_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            success=success,
            error_message=error_message,
            endpoint=endpoint,
            session_id=session_id
        )
        
        db.add(usage)
        db.commit()
        db.refresh(usage)
        
        return usage

    @staticmethod
    def get_tenant_usage(
        db: Session,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[LLMUsage]:
        """Get LLM usage records for a tenant"""
        query = db.query(LLMUsage).filter(LLMUsage.tenant_id == tenant_id)
        
        if start_date:
            query = query.filter(LLMUsage.timestamp >= start_date)
        if end_date:
            query = query.filter(LLMUsage.timestamp <= end_date)
        
        return query.order_by(LLMUsage.timestamp.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_usage_summary(
        db: Session,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> LLMUsageSummary:
        """Get aggregated usage summary for a tenant"""
        query = db.query(
            func.count(LLMUsage.id).label('total_calls'),
            func.sum(func.cast(LLMUsage.success, Integer)).label('successful_calls'),
            func.sum(LLMUsage.input_tokens).label('total_input_tokens'),
            func.sum(LLMUsage.output_tokens).label('total_output_tokens'),
            func.sum(LLMUsage.total_tokens).label('total_tokens'),
            func.sum(LLMUsage.cost_usd).label('total_cost_usd'),
            func.avg(LLMUsage.latency_ms).label('average_latency_ms')
        ).filter(LLMUsage.tenant_id == tenant_id)
        
        if start_date:
            query = query.filter(LLMUsage.timestamp >= start_date)
        if end_date:
            query = query.filter(LLMUsage.timestamp <= end_date)
        
        result = query.first()
        
        total_calls = result.total_calls or 0
        successful_calls = result.successful_calls or 0
        
        return LLMUsageSummary(
            total_calls=total_calls,
            successful_calls=successful_calls,
            failed_calls=total_calls - successful_calls,
            total_input_tokens=result.total_input_tokens or 0,
            total_output_tokens=result.total_output_tokens or 0,
            total_tokens=result.total_tokens or 0,
            total_cost_usd=result.total_cost_usd or Decimal("0.0"),
            average_latency_ms=float(result.average_latency_ms) if result.average_latency_ms else None
        )
    
    @staticmethod
    def get_usage_by_model(
        db: Session,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[LLMUsageByModel]:
        """Get usage breakdown by model"""
        query = db.query(
            LLMUsage.model,
            func.count(LLMUsage.id).label('call_count'),
            func.sum(LLMUsage.total_tokens).label('total_tokens'),
            func.sum(LLMUsage.cost_usd).label('total_cost_usd')
        ).filter(LLMUsage.tenant_id == tenant_id)
        
        if start_date:
            query = query.filter(LLMUsage.timestamp >= start_date)
        if end_date:
            query = query.filter(LLMUsage.timestamp <= end_date)
        
        results = query.group_by(LLMUsage.model).all()
        
        return [
            LLMUsageByModel(
                model=r.model,
                call_count=r.call_count,
                total_tokens=r.total_tokens or 0,
                total_cost_usd=r.total_cost_usd or Decimal("0.0")
            )
            for r in results
        ]
    
    @staticmethod
    def get_usage_by_operation(
        db: Session,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[LLMUsageByOperation]:
        """Get usage breakdown by operation type"""
        query = db.query(
            LLMUsage.operation_type,
            func.count(LLMUsage.id).label('call_count'),
            func.sum(LLMUsage.total_tokens).label('total_tokens'),
            func.sum(LLMUsage.cost_usd).label('total_cost_usd')
        ).filter(LLMUsage.tenant_id == tenant_id)
        
        if start_date:
            query = query.filter(LLMUsage.timestamp >= start_date)
        if end_date:
            query = query.filter(LLMUsage.timestamp <= end_date)
        
        results = query.group_by(LLMUsage.operation_type).all()
        
        return [
            LLMUsageByOperation(
                operation_type=r.operation_type,
                call_count=r.call_count,
                total_tokens=r.total_tokens or 0,
                total_cost_usd=r.total_cost_usd or Decimal("0.0")
            )
            for r in results
        ]
    
    @staticmethod
    def get_all_tenants_usage(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[int, LLMUsageSummary]:
        """Get usage summary for all tenants (admin only)"""
        query = db.query(
            LLMUsage.tenant_id,
            func.count(LLMUsage.id).label('total_calls'),
            func.sum(func.cast(LLMUsage.success, Integer)).label('successful_calls'),
            func.sum(LLMUsage.input_tokens).label('total_input_tokens'),
            func.sum(LLMUsage.output_tokens).label('total_output_tokens'),
            func.sum(LLMUsage.total_tokens).label('total_tokens'),
            func.sum(LLMUsage.cost_usd).label('total_cost_usd'),
            func.avg(LLMUsage.latency_ms).label('average_latency_ms')
        )
        
        if start_date:
            query = query.filter(LLMUsage.timestamp >= start_date)
        if end_date:
            query = query.filter(LLMUsage.timestamp <= end_date)
        
        results = query.group_by(LLMUsage.tenant_id).all()
        
        return {
            r.tenant_id: LLMUsageSummary(
                total_calls=r.total_calls or 0,
                successful_calls=r.successful_calls or 0,
                failed_calls=(r.total_calls or 0) - (r.successful_calls or 0),
                total_input_tokens=r.total_input_tokens or 0,
                total_output_tokens=r.total_output_tokens or 0,
                total_tokens=r.total_tokens or 0,
                total_cost_usd=r.total_cost_usd or Decimal("0.0"),
                average_latency_ms=float(r.average_latency_ms) if r.average_latency_ms else None
            )
            for r in results
        }


# Context manager for tracking LLM calls
class LLMCallTracker:
    """Context manager to automatically track LLM calls"""
    
    def __init__(
        self,
        db: Session,
        tenant_id: str,
        model: str,
        operation_type: str,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        self.db = db
        self.tenant_id = tenant_id
        self.model = model
        self.operation_type = operation_type
        self.user_id = user_id
        self.endpoint = endpoint
        self.session_id = session_id
        self.start_time = None
        self.input_tokens = 0
        self.output_tokens = 0
        self.success = True
        self.error_message = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        latency_ms = int((time.time() - self.start_time) * 1000)
        
        if exc_type is not None:
            self.success = False
            self.error_message = str(exc_val)
        
        try:
            LLMTrackingService.track_llm_call(
                db=self.db,
                tenant_id=self.tenant_id,
                model=self.model,
                operation_type=self.operation_type,
                input_tokens=self.input_tokens,
                output_tokens=self.output_tokens,
                success=self.success,
                error_message=self.error_message,
                latency_ms=latency_ms,
                user_id=self.user_id,
                endpoint=self.endpoint,
                session_id=self.session_id
            )
        except Exception as e:
            # Don't let tracking errors break the main flow
            print(f"Error tracking LLM usage: {e}")
        
        return False  # Don't suppress exceptions
    
    def set_tokens(self, input_tokens: int, output_tokens: int):
        """Set token counts after LLM call"""
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

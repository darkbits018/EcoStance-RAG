from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.auth.dependencies import get_current_user, require_admin
from app.schemas.llm_usage import (
    LLMUsageResponse,
    LLMUsageSummary,
    LLMUsageByModel,
    LLMUsageByOperation
)
from app.services.llm_tracking_service import LLMTrackingService

router = APIRouter(prefix="/api/llm-usage", tags=["LLM Usage"])

@router.get("/", response_model=List[LLMUsageResponse])
def get_my_llm_usage(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get LLM usage records for current user's tenant"""
    usage_records = LLMTrackingService.get_tenant_usage(
        db=db,
        tenant_id=current_user["tenant_id"],
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    return usage_records

@router.get("/summary", response_model=LLMUsageSummary)
def get_my_llm_usage_summary(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get aggregated LLM usage summary for current user's tenant"""
    summary = LLMTrackingService.get_usage_summary(
        db=db,
        tenant_id=current_user["tenant_id"],
        start_date=start_date,
        end_date=end_date
    )
    return summary

@router.get("/by-model", response_model=List[LLMUsageByModel])
def get_my_llm_usage_by_model(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get LLM usage breakdown by model for current user's tenant"""
    usage_by_model = LLMTrackingService.get_usage_by_model(
        db=db,
        tenant_id=current_user["tenant_id"],
        start_date=start_date,
        end_date=end_date
    )
    return usage_by_model

@router.get("/by-operation", response_model=List[LLMUsageByOperation])
def get_my_llm_usage_by_operation(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get LLM usage breakdown by operation type for current user's tenant"""
    usage_by_operation = LLMTrackingService.get_usage_by_operation(
        db=db,
        tenant_id=current_user["tenant_id"],
        start_date=start_date,
        end_date=end_date
    )
    return usage_by_operation

# Admin endpoints
@router.get("/admin/all-tenants", response_model=dict)
def get_all_tenants_llm_usage(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get LLM usage summary for all tenants (admin only)"""
    all_usage = LLMTrackingService.get_all_tenants_usage(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return all_usage

@router.get("/admin/tenant/{tenant_id}/summary", response_model=LLMUsageSummary)
def get_tenant_llm_usage_summary(
    tenant_id: int,
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get LLM usage summary for a specific tenant (admin only)"""
    summary = LLMTrackingService.get_usage_summary(
        db=db,
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date
    )
    return summary

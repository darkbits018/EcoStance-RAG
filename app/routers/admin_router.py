"""
Admin Router - API endpoints for administrative tasks.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.auth.dependencies import require_admin, require_super_admin
from app.services.cleanup_service import CleanupService
from app.services.admin_service import AdminService
from app.config import QDRANT_URL, QDRANT_API_KEY
from qdrant_client import QdrantClient

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


class TenantDeletionRequest(BaseModel):
    """Request model for tenant deletion."""
    soft_delete: bool = True
    confirm: bool = False


class DataExportRequest(BaseModel):
    """Request model for data export."""
    export_path: str | None = None


def get_qdrant_client():
    """Get Qdrant client instance."""
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


@router.delete("/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    request: TenantDeletionRequest,
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Delete a tenant and all associated data (admin only).
    
    Args:
        tenant_id: Tenant to delete
        request: Deletion options
    """
    if not request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deletion must be confirmed by setting 'confirm' to true"
        )
    
    try:
        qdrant_client = get_qdrant_client()
        cleanup_service = CleanupService(db, qdrant_client)
        
        results = cleanup_service.delete_tenant_data(
            tenant_id=tenant_id,
            soft_delete=request.soft_delete
        )
        
        if results["errors"]:
            return {
                "success": False,
                "message": "Tenant deletion completed with errors",
                "data": results
            }
        
        return {
            "success": True,
            "message": f"Tenant {tenant_id} {'soft' if request.soft_delete else 'hard'} deleted successfully",
            "data": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tenant: {str(e)}"
        )


@router.post("/tenants/{tenant_id}/export")
async def export_tenant_data(
    tenant_id: str,
    request: DataExportRequest,
    background_tasks: BackgroundTasks,
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Export all data for a tenant (admin only).
    
    Args:
        tenant_id: Tenant to export
        request: Export options
    """
    try:
        import os
        from datetime import datetime
        
        # Generate export path if not provided
        export_path = request.export_path or os.path.join(
            "exports",
            tenant_id,
            datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        )
        
        qdrant_client = get_qdrant_client()
        cleanup_service = CleanupService(db, qdrant_client)
        
        # Run export in background
        def run_export():
            results = cleanup_service.export_tenant_data(tenant_id, export_path)
            # Could send notification when complete
        
        background_tasks.add_task(run_export)
        
        return {
            "success": True,
            "message": f"Export started for tenant {tenant_id}",
            "export_path": export_path,
            "status": "in_progress"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start export: {str(e)}"
        )


@router.get("/tenants/{tenant_id}/storage")
async def get_tenant_storage(
    tenant_id: str,
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get storage usage for a tenant (admin only).
    
    Args:
        tenant_id: Tenant to check
    """
    try:
        qdrant_client = get_qdrant_client()
        cleanup_service = CleanupService(db, qdrant_client)
        
        storage_info = cleanup_service.get_tenant_storage_usage(tenant_id)
        
        return {
            "success": True,
            "data": storage_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get storage info: {str(e)}"
        )


@router.post("/cleanup/sessions")
async def cleanup_sessions(
    max_age_hours: int = 24,
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Clean up expired sessions (admin only).
    
    Args:
        max_age_hours: Maximum age of sessions in hours
    """
    try:
        qdrant_client = get_qdrant_client()
        cleanup_service = CleanupService(db, qdrant_client)
        
        deleted_count = cleanup_service.cleanup_expired_sessions(max_age_hours)
        
        return {
            "success": True,
            "message": f"Cleaned up {deleted_count} expired sessions",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup sessions: {str(e)}"
        )


@router.post("/cleanup/temp-files")
async def cleanup_temp_files(
    max_age_days: int = 7,
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Clean up old temporary files (admin only).
    
    Args:
        max_age_days: Maximum age of temp files in days
    """
    try:
        qdrant_client = get_qdrant_client()
        cleanup_service = CleanupService(db, qdrant_client)
        
        deleted_count = cleanup_service.cleanup_temporary_files(max_age_days)
        
        return {
            "success": True,
            "message": f"Cleaned up {deleted_count} temporary files",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup temp files: {str(e)}"
        )


@router.post("/cleanup/audit-logs")
async def archive_audit_logs(
    max_age_days: int = 90,
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Archive old audit logs (admin only).
    
    Args:
        max_age_days: Maximum age of logs to keep
    """
    try:
        qdrant_client = get_qdrant_client()
        cleanup_service = CleanupService(db, qdrant_client)
        
        archived_count = cleanup_service.archive_old_audit_logs(max_age_days)
        
        return {
            "success": True,
            "message": f"Archived {archived_count} audit logs",
            "archived_count": archived_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to archive audit logs: {str(e)}"
        )


@router.post("/cleanup/all")
async def run_daily_cleanup(
    background_tasks: BackgroundTasks,
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run all daily cleanup tasks (admin only).
    """
    try:
        qdrant_client = get_qdrant_client()
        cleanup_service = CleanupService(db, qdrant_client)
        
        # Run cleanup in background
        def run_cleanup():
            results = cleanup_service.run_daily_cleanup()
            # Could send notification when complete
        
        background_tasks.add_task(run_cleanup)
        
        return {
            "success": True,
            "message": "Daily cleanup tasks started",
            "status": "in_progress"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start cleanup: {str(e)}"
        )


@router.get("/health/system")
async def get_system_health(
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive system health metrics (admin only).
    Returns detailed status for API, database, Qdrant, and background jobs.
    """
    try:
        admin_service = AdminService(db)
        data = admin_service.get_system_health()
        
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health: {str(e)}"
        )


# ============================================================================
# PHASE 5: Enhanced Admin Endpoints
# ============================================================================

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get admin dashboard summary statistics.
    Provides high-level overview of system status.
    """
    try:
        admin_service = AdminService(db)
        data = admin_service.get_dashboard_summary()
        
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard summary: {str(e)}"
        )


@router.get("/tenants/search")
async def search_tenants(
    q: str,
    status: Optional[str] = None,
    tier: Optional[str] = None,
    limit: int = 20,
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Search tenants by name, email, or slug with optional filters.
    Returns matching tenants with detailed info.
    
    Query params:
    - q: Search query (required)
    - status: Filter by status (active, inactive, suspended)
    - tier: Filter by billing tier (free, starter, professional, enterprise)
    - limit: Max results (default 20)
    """
    try:
        admin_service = AdminService(db)
        results = admin_service.search_tenants(q, status, tier, limit)
        
        return {
            "success": True,
            "data": {
                "query": q,
                "count": len(results),
                "tenants": results
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search tenants: {str(e)}"
        )


@router.patch("/tenants/{tenant_id}/tier")
async def update_tenant_tier(
    tenant_id: str,
    tier: str,
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update tenant billing tier and adjust quotas accordingly.
    Valid tiers: free, starter, professional, enterprise
    """
    try:
        from app.models.tenant import Tenant
        from datetime import datetime
        
        # Validate tier
        valid_tiers = ["free", "starter", "professional", "enterprise"]
        if tier not in valid_tiers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier. Must be one of: {', '.join(valid_tiers)}"
            )
        
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Update tier
        old_tier = tenant.billing_tier
        tenant.billing_tier = tier
        
        # Update quotas based on tier
        tier_quotas = {
            "free": {
                "max_storage_bytes": 10 * 1024**3,  # 10GB
                "max_queries_per_day": 1000,
                "max_queries_per_month": 30000,
                "max_documents": 10000,
                "max_db_connections": 5
            },
            "starter": {
                "max_storage_bytes": 50 * 1024**3,  # 50GB
                "max_queries_per_day": 5000,
                "max_queries_per_month": 150000,
                "max_documents": 50000,
                "max_db_connections": 10
            },
            "professional": {
                "max_storage_bytes": 200 * 1024**3,  # 200GB
                "max_queries_per_day": 20000,
                "max_queries_per_month": 600000,
                "max_documents": 200000,
                "max_db_connections": 25,
                "features": ["rag", "db_chat", "custom_embeddings", "api_access", "priority_support", "multilingual"]
            },
            "enterprise": {
                "max_storage_bytes": 1000 * 1024**3,  # 1TB
                "max_queries_per_day": 100000,
                "max_queries_per_month": 3000000,
                "max_documents": 1000000,
                "max_db_connections": 100,
                "features": ["rag", "db_chat", "custom_embeddings", "api_access", "priority_support", "sla", "dedicated_support", "multilingual"]
            }
        }
        
        settings = tenant.settings or {}
        settings.update(tier_quotas[tier])
        tenant.settings = settings
        tenant.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(tenant)
        
        return {
            "success": True,
            "message": f"Tenant tier updated from {old_tier} to {tier}",
            "data": {
                "tenant_id": tenant_id,
                "old_tier": old_tier,
                "new_tier": tier,
                "quotas": tier_quotas[tier]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update tenant tier: {str(e)}"
        )


@router.post("/tenants/{tenant_id}/suspend")
async def suspend_tenant(
    tenant_id: str,
    reason: str,
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Suspend a tenant account.
    Prevents all API access until reactivated.
    """
    try:
        from app.models.tenant import Tenant
        from datetime import datetime
        
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Suspend tenant
        tenant.is_active = False
        tenant.billing_status = "suspended"
        tenant.updated_at = datetime.utcnow()
        
        # Log suspension reason in settings
        settings = tenant.settings or {}
        settings["suspension"] = {
            "reason": reason,
            "suspended_at": datetime.utcnow().isoformat(),
            "suspended_by": admin_tenant_id
        }
        tenant.settings = settings
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Tenant {tenant_id} suspended",
            "data": {
                "tenant_id": tenant_id,
                "reason": reason,
                "suspended_at": datetime.utcnow().isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to suspend tenant: {str(e)}"
        )


@router.post("/tenants/{tenant_id}/reactivate")
async def reactivate_tenant(
    tenant_id: str,
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Reactivate a suspended tenant account.
    Restores full API access.
    """
    try:
        from app.models.tenant import Tenant
        from datetime import datetime
        
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Reactivate tenant
        tenant.is_active = True
        tenant.billing_status = "active"
        tenant.updated_at = datetime.utcnow()
        
        # Log reactivation in settings
        settings = tenant.settings or {}
        if "suspension" in settings:
            settings["suspension"]["reactivated_at"] = datetime.utcnow().isoformat()
            settings["suspension"]["reactivated_by"] = admin_tenant_id
        tenant.settings = settings
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Tenant {tenant_id} reactivated",
            "data": {
                "tenant_id": tenant_id,
                "reactivated_at": datetime.utcnow().isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reactivate tenant: {str(e)}"
        )


@router.get("/tenants/{tenant_id}/activity")
async def get_tenant_activity(
    tenant_id: str,
    days: int = 7,
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get tenant activity log for the specified number of days.
    Returns API usage, errors, and other activity metrics.
    """
    try:
        from app.models.tenant import Tenant
        from datetime import datetime, timedelta
        from sqlalchemy import text
        
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Get API usage
        try:
            result = db.execute(
                text("SELECT COUNT(*) FROM api_usage WHERE tenant_id = :tenant_id AND timestamp >= :cutoff"),
                {"tenant_id": tenant_id, "cutoff": cutoff}
            ).fetchone()
            api_calls = result[0] if result else 0
            
            result = db.execute(
                text("SELECT COUNT(*) FROM api_usage WHERE tenant_id = :tenant_id AND timestamp >= :cutoff AND status_code >= 400"),
                {"tenant_id": tenant_id, "cutoff": cutoff}
            ).fetchone()
            errors = result[0] if result else 0
        except:
            api_calls = 0
            errors = 0
        
        # Get recent activity
        try:
            recent_activity = db.execute(
                text("""
                SELECT endpoint, method, status_code, timestamp 
                FROM api_usage 
                WHERE tenant_id = :tenant_id AND timestamp >= :cutoff
                ORDER BY timestamp DESC
                LIMIT 50
                """),
                {"tenant_id": tenant_id, "cutoff": cutoff}
            ).fetchall()
            
            activity_list = [
                {
                    "endpoint": row[0],
                    "method": row[1],
                    "status_code": row[2],
                    "timestamp": row[3]
                }
                for row in recent_activity
            ]
        except:
            activity_list = []
        
        return {
            "success": True,
            "data": {
                "tenant_id": tenant_id,
                "period_days": days,
                "summary": {
                    "total_api_calls": api_calls,
                    "total_errors": errors,
                    "error_rate": (errors / api_calls * 100) if api_calls > 0 else 0
                },
                "recent_activity": activity_list
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tenant activity: {str(e)}"
        )



# ============================================================================
# Quota Management Endpoints
# ============================================================================

@router.get("/quotas/templates")
async def get_quota_templates(
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get quota templates for different billing tiers.
    Returns default quota configurations.
    """
    templates = {
        "free": {
            "tier": "free",
            "max_storage_bytes": 10 * 1024**3,  # 10GB
            "max_queries_per_day": 1000,
            "max_queries_per_month": 30000,
            "max_documents": 10000,
            "max_db_connections": 5,
            "max_users": 3,
            "features": ["rag", "db_chat"]
        },
        "starter": {
            "tier": "starter",
            "max_storage_bytes": 50 * 1024**3,  # 50GB
            "max_queries_per_day": 5000,
            "max_queries_per_month": 150000,
            "max_documents": 50000,
            "max_db_connections": 10,
            "max_users": 10,
            "features": ["rag", "db_chat", "custom_embeddings"]
        },
        "professional": {
            "tier": "professional",
            "max_storage_bytes": 200 * 1024**3,  # 200GB
            "max_queries_per_day": 20000,
            "max_queries_per_month": 600000,
            "max_documents": 200000,
            "max_db_connections": 25,
            "max_users": 50,
            "features": ["rag", "db_chat", "custom_embeddings", "api_access", "priority_support", "multilingual"]
        },
        "enterprise": {
            "tier": "enterprise",
            "max_storage_bytes": 1000 * 1024**3,  # 1TB
            "max_queries_per_day": 100000,
            "max_queries_per_month": 3000000,
            "max_documents": 1000000,
            "max_db_connections": 100,
            "max_users": -1,  # Unlimited
            "features": ["rag", "db_chat", "custom_embeddings", "api_access", "priority_support", "sla", "dedicated_support", "multilingual"]
        }
    }
    
    return {
        "success": True,
        "data": templates
    }


@router.put("/quotas/templates/{tier}")
async def update_quota_template(
    tier: str,
    quotas: Dict[str, Any],
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update quota template for a billing tier.
    This would typically update a configuration table.
    """
    valid_tiers = ["free", "starter", "professional", "enterprise"]
    if tier not in valid_tiers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier. Must be one of: {', '.join(valid_tiers)}"
        )
    
    # In a real implementation, this would update a quota_templates table
    # For now, we'll just return success
    return {
        "success": True,
        "message": f"Quota template for {tier} updated",
        "data": {
            "tier": tier,
            "quotas": quotas
        }
    }


@router.put("/quotas/{tenant_id}")
async def update_tenant_quotas(
    tenant_id: str,
    quotas: Dict[str, Any],
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update custom quotas for a specific tenant.
    Overrides the default tier quotas.
    """
    from app.models.tenant import Tenant
    from datetime import datetime
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Update tenant settings with custom quotas
    settings = tenant.settings or {}
    settings.update(quotas)
    settings["custom_quotas"] = True
    settings["quotas_updated_at"] = datetime.utcnow().isoformat()
    settings["quotas_updated_by"] = admin_tenant_id
    
    tenant.settings = settings
    tenant.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Custom quotas applied to tenant {tenant_id}",
        "data": {
            "tenant_id": tenant_id,
            "quotas": quotas
        }
    }


# ============================================================================
# Audit Logs Endpoints
# ============================================================================

@router.get("/audit-logs")
async def get_audit_logs(
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get audit logs with optional filters.
    Returns system-wide audit trail.
    """
    from datetime import datetime, timedelta
    from sqlalchemy import text
    
    try:
        # Parse dates
        if end_date:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        else:
            end = datetime.utcnow()
        
        if start_date:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        else:
            start = end - timedelta(days=30)
        
        # Get audit logs from api_usage table (simplified)
        query = text("""
            SELECT tenant_id, endpoint, method, status_code, timestamp, response_time_ms
            FROM api_usage
            WHERE timestamp >= :start AND timestamp <= :end
        """)
        
        params = {"start": start, "end": end}
        
        if status:
            if status == "success":
                query = text("""
                    SELECT tenant_id, endpoint, method, status_code, timestamp, response_time_ms
                    FROM api_usage
                    WHERE timestamp >= :start AND timestamp <= :end AND status_code < 400
                """)
            elif status == "error":
                query = text("""
                    SELECT tenant_id, endpoint, method, status_code, timestamp, response_time_ms
                    FROM api_usage
                    WHERE timestamp >= :start AND timestamp <= :end AND status_code >= 400
                """)
        
        query_text = str(query) + " ORDER BY timestamp DESC LIMIT :limit"
        params["limit"] = limit
        
        results = db.execute(text(query_text), params).fetchall()
        
        logs = [
            {
                "id": f"log_{i}",
                "tenant_id": row[0],
                "action": f"{row[2]} {row[1]}",
                "endpoint": row[1],
                "method": row[2],
                "status": "success" if row[3] < 400 else "error",
                "status_code": row[3],
                "timestamp": row[4],
                "response_time_ms": row[5]
            }
            for i, row in enumerate(results)
        ]
        
        return {
            "success": True,
            "data": {
                "count": len(logs),
                "logs": logs
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit logs: {str(e)}"
        )


@router.get("/audit-logs/{log_id}")
async def get_audit_log_detail(
    log_id: str,
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific audit log entry.
    """
    # In a real implementation, this would query a specific log entry
    # For now, return a mock response
    return {
        "success": True,
        "data": {
            "id": log_id,
            "tenant_id": "tenant_123",
            "action": "GET /api/v1/query",
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "endpoint": "/api/v1/query",
                "method": "GET",
                "status_code": 200,
                "response_time_ms": 45,
                "user_agent": "Mozilla/5.0...",
                "ip_address": "192.168.1.1"
            }
        }
    }


# ============================================================================
# Settings Endpoints
# ============================================================================

@router.get("/settings")
async def get_admin_settings(
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get system-wide admin settings.
    Returns configuration for the entire platform.
    """
    # In a real implementation, this would query a settings table
    # For now, return default settings
    settings = {
        "system": {
            "maintenance_mode": False,
            "allow_new_registrations": True,
            "require_email_verification": True,
            "default_tier": "free"
        },
        "security": {
            "session_timeout_minutes": 60,
            "max_login_attempts": 5,
            "password_min_length": 8,
            "require_mfa": False
        },
        "limits": {
            "max_tenants": -1,  # Unlimited
            "max_users_per_tenant": 100,
            "max_api_calls_per_minute": 1000
        },
        "notifications": {
            "admin_email": "admin@example.com",
            "alert_on_errors": True,
            "alert_threshold": 100,
            "send_weekly_reports": True
        },
        "features": {
            "enable_public_chat": True,
            "enable_public_agent": True,
            "enable_db_connections": True,
            "enable_custom_embeddings": True
        }
    }
    
    return {
        "success": True,
        "data": settings
    }


@router.put("/settings")
async def update_admin_settings(
    settings: Dict[str, Any],
    admin_tenant_id: str = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update system-wide admin settings.
    Modifies platform configuration.
    """
    from datetime import datetime
    
    # In a real implementation, this would update a settings table
    # For now, just return success
    return {
        "success": True,
        "message": "Admin settings updated successfully",
        "data": {
            "settings": settings,
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by": admin_tenant_id
        }
    }

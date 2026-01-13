"""
Dynamics 365 API Router.
Handles configuration and manual sync triggers for Dynamics CRM.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict

from app.db.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.rbac import RBACService
from app.auth.permissions import Permission
from app.services.dynamics_auth_service import DynamicsAuthService
from app.services.dynamics_fetch_service import DynamicsFetchService
from app.schemas.dynamics import (
    DynamicsConfigCreate, 
    DynamicsConfigResponse, 
    DynamicsTestResponse
)

router = APIRouter(prefix="/api/v1/dynamics", tags=["Dynamics 365 Integration"])

@router.post("/config", response_model=DynamicsConfigResponse)
async def configure_dynamics(
    config_data: DynamicsConfigCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Configure Dynamics 365 credentials for the tenant.
    Requires: DYNAMICS_CONFIGURE permission
    """
    rbac = RBACService(db)
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.DYNAMICS_CONFIGURE
    )
    
    auth_service = DynamicsAuthService(db)
    
    # Save config
    config_dict = config_data.model_dump()
    auth_service.save_config(current_user["tenant_id"], config_dict)
    
    return {
        "tenant_id": config_data.tenant_id,
        "client_id": config_data.client_id,
        "resource_url": config_data.resource_url,
        "is_configured": True
    }

@router.get("/config", response_model=DynamicsConfigResponse)
async def get_dynamics_config(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current Dynamics 365 configuration status.
    Requires: DYNAMICS_CONFIGURE permission
    """
    rbac = RBACService(db)
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.DYNAMICS_CONFIGURE
    )
    
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.id == current_user["tenant_id"]).first()
    
    config = tenant.dynamics_config or {}
    
    return {
        "tenant_id": config.get("tenant_id", ""),
        "client_id": config.get("client_id", ""),
        "resource_url": config.get("resource_url", ""),
        "is_configured": bool(config.get("client_id")),
        "last_sync": None  # Todo: fetch from logs
    }

@router.post("/test", response_model=DynamicsTestResponse)
async def test_connection(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Test connectivity to Dynamics 365.
    Requires: DYNAMICS_CONFIGURE permission
    """
    rbac = RBACService(db)
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.DYNAMICS_CONFIGURE
    )
    
    auth_service = DynamicsAuthService(db)
    
    try:
        # 1. Try to get a valid token
        token = auth_service.get_token(current_user["tenant_id"])
        
        # 2. Try to fetch 1 email to verify API access
        from app.models.tenant import Tenant
        tenant = db.query(Tenant).filter(Tenant.id == current_user["tenant_id"]).first()
        resource_url = tenant.dynamics_config.get('resource_url')
        
        fetch_service = DynamicsFetchService(resource_url, token)
        emails = fetch_service.fetch_recent_emails(lookback_minutes=10)
        
        return {
            "success": True,
            "message": f"Successfully connected. Found {len(emails)} recent emails."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection failed: {str(e)}"
        }

@router.post("/sync/now")
async def sync_now(
    lookback_minutes: int = 60,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Manually trigger a sync of Dynamics emails.
    Requires: DYNAMICS_SYNC permission
    """
    rbac = RBACService(db)
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.DYNAMICS_SYNC
    )
    
    from app.services.dynamics_rag_service import DynamicsRAGService
    from app.models.tenant import Tenant
    
    # 1. Get Config & Token
    tenant = db.query(Tenant).filter(Tenant.id == current_user["tenant_id"]).first()
    if not tenant or not tenant.dynamics_config or 'client_id' not in tenant.dynamics_config:
        raise HTTPException(status_code=400, detail="Dynamics 365 not configured")
        
    auth_service = DynamicsAuthService(db)
    try:
        token = auth_service.get_token(current_user["tenant_id"])
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {e}")
        
    # 2. Fetch
    try:
        resource_url = tenant.dynamics_config.get('resource_url')
        fetch_service = DynamicsFetchService(resource_url, token)
        emails = fetch_service.fetch_recent_emails(lookback_minutes=lookback_minutes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fetch failed: {e}")
        
    # 3. Process
    if not emails:
        return {"message": "No new emails found within the lookback period."}
        
    try:
        rag_service = DynamicsRAGService(db, current_user["tenant_id"])
        chunks = rag_service.process_emails_to_kb(emails)
        
        return {
            "message": "Sync completed successfully",
            "emails_found": len(emails),
            "chunks_created": chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

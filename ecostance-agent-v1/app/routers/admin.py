"""
System Administration API endpoints.
Super Admin only endpoints for managing tenants and system roles.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.auth.rbac import RBACService
from app.auth.permissions import Permission, SystemRole
from app.models.tenant import Tenant
from app.models.tenant_user import TenantUser
from app.auth.dependencies import require_super_admin, get_current_user

router = APIRouter(prefix="/api/v1/admin", tags=["System Administration"])


class PromoteUserRequest(BaseModel):
    """Request schema for promoting a user to tenant admin."""
    user_id: str
    role: SystemRole


class TenantSummary(BaseModel):
    """Summary information about a tenant."""
    id: str
    name: str
    is_active: bool
    user_count: int
    created_at: str
    
    class Config:
        from_attributes = True


# Removed insecure placeholder get_current_user_info


@router.get("/tenants", response_model=List[TenantSummary])
async def list_all_tenants(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _: str = Depends(require_super_admin)
):
    """
    List all tenants in the system.
    
    Requires: ADMIN_VIEW_ALL permission (Super Admin only)
    """
    rbac = RBACService(db)
    
    # Check if user has super admin permissions
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.ADMIN_VIEW_ALL
    )
    
    try:
        # Get all tenants with user counts
        tenants = db.query(Tenant).all()
        
        tenant_summaries = []
        for tenant in tenants:
            user_count = db.query(TenantUser).filter(
                TenantUser.tenant_id == tenant.id
            ).count()
            
            tenant_summaries.append(TenantSummary(
                id=tenant.id,
                name=tenant.name,
                is_active=getattr(tenant, 'is_active', True),  # Default to True if field doesn't exist
                user_count=user_count,
                created_at=tenant.created_at.isoformat() if hasattr(tenant, 'created_at') and tenant.created_at else ""
            ))
        
        return tenant_summaries
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tenants: {str(e)}"
        )


@router.get("/tenants/{tenant_id}/users")
async def list_tenant_users_admin(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _: str = Depends(require_super_admin)
):
    """
    List all users in a specific tenant (Super Admin view).
    
    Requires: ADMIN_MANAGE_USERS permission (Super Admin only)
    """
    rbac = RBACService(db)
    
    # Check if user has super admin permissions
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.ADMIN_MANAGE_USERS
    )
    
    try:
        # Verify tenant exists
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Get all users in the tenant
        users = db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id
        ).all()
        
        user_details = []
        for user in users:
            user_dict = user.to_dict()
            
            # Add role information
            if user.tenant_role:
                user_dict["role_info"] = {
                    "type": "tenant_role",
                    "role_name": user.tenant_role.name,
                    "role_description": user.tenant_role.description
                }
            elif user.system_role:
                user_dict["role_info"] = {
                    "type": "system_role",
                    "role_name": user.system_role.replace("_", " ").title()
                }
            elif user.role:
                user_dict["role_info"] = {
                    "type": "legacy_role",
                    "role_name": user.role.replace("_", " ").title()
                }
            else:
                user_dict["role_info"] = {
                    "type": "no_role",
                    "role_name": "No Role Assigned"
                }
            
            user_details.append(user_dict)
        
        return {
            "tenant": {
                "id": tenant.id,
                "name": tenant.name
            },
            "users": user_details,
            "total_users": len(user_details)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tenant users: {str(e)}"
        )


@router.post("/tenants/{tenant_id}/promote-admin")
async def promote_user_to_admin(
    tenant_id: str,
    request: PromoteUserRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _: str = Depends(require_super_admin)
):
    """
    Promote a user to tenant admin or super admin.
    
    Requires: ADMIN_MANAGE_USERS permission (Super Admin only)
    """
    rbac = RBACService(db)
    
    # Check if user has super admin permissions
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.ADMIN_MANAGE_USERS
    )
    
    try:
        # Verify tenant exists
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Verify user exists in tenant
        tenant_user = db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == request.user_id
        ).first()
        
        if not tenant_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in tenant"
            )
        
        # Assign system role
        updated_user = rbac.assign_system_role(
            tenant_id=tenant_id,
            user_id=request.user_id,
            system_role=request.role,
            assigned_by=current_user["user_id"]
        )
        
        return {
            "message": f"User promoted to {request.role.value} successfully",
            "user": updated_user.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to promote user: {str(e)}"
        )


@router.get("/system/roles")
async def view_system_role_assignments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _: str = Depends(require_super_admin)
):
    """
    View all system role assignments across all tenants.
    
    Requires: ADMIN_VIEW_ALL permission (Super Admin only)
    """
    rbac = RBACService(db)
    
    # Check if user has super admin permissions
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.ADMIN_VIEW_ALL
    )
    
    try:
        # Get all users with system roles
        system_users = db.query(TenantUser).filter(
            TenantUser.system_role.isnot(None)
        ).all()
        
        role_assignments = {}
        
        for user in system_users:
            role = user.system_role
            if role not in role_assignments:
                role_assignments[role] = {
                    "role": role,
                    "role_name": role.replace("_", " ").title(),
                    "users": []
                }
            
            # Get tenant info
            tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
            
            role_assignments[role]["users"].append({
                "user_id": user.user_id,
                "email": user.email,
                "full_name": user.full_name,
                "tenant_id": user.tenant_id,
                "tenant_name": tenant.name if tenant else "Unknown",
                "created_at": user.created_at.isoformat() if user.created_at else None
            })
        
        return {
            "system_roles": list(role_assignments.values()),
            "total_roles": len(role_assignments),
            "total_users": len(system_users)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to view system roles: {str(e)}"
        )


@router.get("/metrics")
async def get_system_metrics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _: str = Depends(require_super_admin)
):
    """
    Get system-wide metrics and statistics.
    
    Requires: ADMIN_VIEW_METRICS permission (Super Admin only)
    """
    rbac = RBACService(db)
    
    # Check if user has super admin permissions
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.ADMIN_VIEW_METRICS
    )
    
    try:
        # Get basic counts
        total_tenants = db.query(Tenant).count()
        total_users = db.query(TenantUser).count()
        
        # Count system role assignments
        super_admins = db.query(TenantUser).filter(
            TenantUser.system_role == SystemRole.SUPER_ADMIN.value
        ).count()
        
        tenant_admins = db.query(TenantUser).filter(
            TenantUser.system_role == SystemRole.TENANT_ADMIN.value
        ).count()
        
        # Count tenant roles
        from app.models.tenant_role import TenantRole
        total_tenant_roles = db.query(TenantRole).count()
        active_tenant_roles = db.query(TenantRole).filter(
            TenantRole.is_active == True
        ).count()
        
        # Users with tenant roles
        users_with_tenant_roles = db.query(TenantUser).filter(
            TenantUser.tenant_role_id.isnot(None)
        ).count()
        
        # Legacy role users
        users_with_legacy_roles = db.query(TenantUser).filter(
            TenantUser.role.isnot(None),
            TenantUser.system_role.is_(None),
            TenantUser.tenant_role_id.is_(None)
        ).count()
        
        return {
            "system_overview": {
                "total_tenants": total_tenants,
                "total_users": total_users,
                "total_tenant_roles": total_tenant_roles,
                "active_tenant_roles": active_tenant_roles
            },
            "role_distribution": {
                "super_admins": super_admins,
                "tenant_admins": tenant_admins,
                "users_with_tenant_roles": users_with_tenant_roles,
                "users_with_legacy_roles": users_with_legacy_roles,
                "users_without_roles": total_users - super_admins - tenant_admins - users_with_tenant_roles - users_with_legacy_roles
            },
            "rbac_migration_status": {
                "migrated_to_new_system": super_admins + tenant_admins + users_with_tenant_roles,
                "still_on_legacy": users_with_legacy_roles,
                "migration_percentage": round(
                    ((super_admins + tenant_admins + users_with_tenant_roles) / total_users * 100) if total_users > 0 else 0,
                    2
                )
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system metrics: {str(e)}"
        )

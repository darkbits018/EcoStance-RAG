"""
Tenant Role Management API endpoints.
Provides CRUD operations for tenant roles and role assignments.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.auth.rbac import RBACService
from app.auth.permissions import Permission
from app.schemas.tenant_role import (
    TenantRoleCreate,
    TenantRoleUpdate,
    TenantRoleResponse,
    TenantRoleListResponse,
    AssignRoleRequest,
    RemoveRoleRequest
)
from app.models.tenant_role import TenantRole
from app.models.tenant_user import TenantUser

from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/tenant", tags=["Tenant Roles"])





@router.get("/roles", response_model=TenantRoleListResponse)
async def list_tenant_roles(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all active roles in the current tenant.
    
    Requires: TENANT_VIEW permission
    """
    rbac = RBACService(db)
    
    try:
        roles = rbac.list_tenant_roles(
            tenant_id=current_user["tenant_id"],
            requester_id=current_user["user_id"]
        )
        
        return TenantRoleListResponse(
            roles=[TenantRoleResponse.from_orm(role) for role in roles],
            total=len(roles)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list roles: {str(e)}"
        )


@router.post("/roles", response_model=TenantRoleResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant_role(
    role_data: TenantRoleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new tenant role with specified permissions.
    
    Requires: TENANT_MANAGE_USERS permission
    """
    rbac = RBACService(db)
    
    try:
        tenant_role = rbac.create_tenant_role(
            tenant_id=current_user["tenant_id"],
            creator_id=current_user["user_id"],
            name=role_data.name,
            permissions=role_data.permissions,
            description=role_data.description
        )
        
        return TenantRoleResponse.from_orm(tenant_role)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create role: {str(e)}"
        )


@router.put("/roles/{role_id}", response_model=TenantRoleResponse)
async def update_tenant_role(
    role_id: str,
    role_data: TenantRoleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing tenant role.
    
    Requires: TENANT_MANAGE_USERS permission
    """
    rbac = RBACService(db)
    
    try:
        tenant_role = rbac.update_tenant_role(
            role_id=role_id,
            updater_id=current_user["user_id"],
            name=role_data.name,
            permissions=role_data.permissions,
            description=role_data.description
        )
        
        return TenantRoleResponse.from_orm(tenant_role)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update role: {str(e)}"
        )


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a tenant role. Users with this role will lose it.
    
    Requires: TENANT_MANAGE_USERS permission
    """
    rbac = RBACService(db)
    
    try:
        rbac.delete_tenant_role(
            role_id=role_id,
            deleter_id=current_user["user_id"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete role: {str(e)}"
        )


@router.get("/roles/{role_id}/users")
async def list_role_users(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all users assigned to a specific role.
    
    Requires: TENANT_VIEW permission
    """
    rbac = RBACService(db)
    
    # Check permission
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.TENANT_VIEW
    )
    
    try:
        # Get the role to verify it exists and belongs to the tenant
        role = db.query(TenantRole).filter(
            TenantRole.id == role_id,
            TenantRole.tenant_id == current_user["tenant_id"]
        ).first()
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Get users with this role
        users = db.query(TenantUser).filter(
            TenantUser.tenant_role_id == role_id,
            TenantUser.tenant_id == current_user["tenant_id"]
        ).all()
        
        return {
            "role": TenantRoleResponse.from_orm(role),
            "users": [user.to_dict() for user in users],
            "total_users": len(users)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list role users: {str(e)}"
        )


@router.post("/users/{user_id}/assign-role", status_code=status.HTTP_200_OK)
async def assign_role_to_user(
    user_id: str,
    request: AssignRoleRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Assign a tenant role to a user.
    
    Requires: TENANT_MANAGE_USERS permission
    """
    rbac = RBACService(db)
    
    try:
        tenant_user = rbac.assign_tenant_role(
            tenant_id=current_user["tenant_id"],
            user_id=user_id,
            role_id=request.role_id,
            assigned_by=current_user["user_id"]
        )
        
        return {
            "message": "Role assigned successfully",
            "user": tenant_user.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign role: {str(e)}"
        )


@router.delete("/users/{user_id}/remove-role", status_code=status.HTTP_200_OK)
async def remove_role_from_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Remove the tenant role from a user.
    
    Requires: TENANT_MANAGE_USERS permission
    """
    rbac = RBACService(db)
    
    # Check permission
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.TENANT_MANAGE_USERS
    )
    
    try:
        # Get the user
        tenant_user = db.query(TenantUser).filter(
            TenantUser.tenant_id == current_user["tenant_id"],
            TenantUser.user_id == user_id
        ).first()
        
        if not tenant_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in tenant"
            )
        
        # Remove the role
        tenant_user.tenant_role_id = None
        db.commit()
        db.refresh(tenant_user)
        
        return {
            "message": "Role removed successfully",
            "user": tenant_user.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove role: {str(e)}"
        )
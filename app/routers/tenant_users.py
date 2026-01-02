from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.rbac import RBACService
from app.auth.permissions import Permission
from app.models.tenant_user import TenantUser
from app.models.tenant_role import TenantRole
from app.schemas.tenant_user import TenantUserCreate, TenantUserUpdate, TenantUserResponse

router = APIRouter(prefix="/api/v1/tenant", tags=["Tenant User Management"])


def _enrich_user(user: TenantUser) -> TenantUser:
    """Attach computed role_name to user object for response model."""
    role_name = None
    if user.tenant_role:
        role_name = user.tenant_role.name
    elif user.system_role:
        role_name = user.system_role
    elif user.role:
        role_name = user.role
        
    setattr(user, "role_name", role_name)
    return user

@router.post("/users", response_model=TenantUserResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant_user(
    user_data: TenantUserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new user within the tenant (Invitation).
    
    Requires: TENANT_MANAGE_USERS permission
    """
    rbac = RBACService(db)
    tenant_id = current_user["tenant_id"]
    
    # Check permission
    rbac.require_permission(
        tenant_id=tenant_id,
        user_id=current_user["user_id"],
        permission=Permission.TENANT_MANAGE_USERS
    )
    
    # Check if user with email already exists in this tenant
    existing_user = db.query(TenantUser).filter(
        TenantUser.tenant_id == tenant_id,
        TenantUser.email == user_data.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists in the tenant"
        )
    
    # Validate role if provided
    tenant_role_id = None
    if user_data.role_id:
        role = db.query(TenantRole).filter(
            TenantRole.id == user_data.role_id,
            TenantRole.tenant_id == tenant_id
        ).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id"
            )
        tenant_role_id = role.id

    # Create new user
    new_user_id = str(uuid.uuid4())
    
    # Hash password
    import bcrypt
    password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    new_tenant_user = TenantUser(
        tenant_id=tenant_id,
        user_id=new_user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=password_hash,
        is_active=user_data.is_active,
        tenant_role_id=tenant_role_id
    )
    
    db.add(new_tenant_user)
    db.commit()
    db.refresh(new_tenant_user)
    
    return _enrich_user(new_tenant_user)

@router.get("/users", response_model=List[TenantUserResponse])
async def list_tenant_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all users in the current tenant.
    
    Requires: TENANT_VIEW permission
    """
    rbac = RBACService(db)
    tenant_id = current_user["tenant_id"]
    
    # Check permission
    rbac.require_permission(
        tenant_id=tenant_id,
        user_id=current_user["user_id"],
        permission=Permission.TENANT_VIEW
    )
    
    tenant_users = db.query(TenantUser).filter(
        TenantUser.tenant_id == tenant_id
    ).all()
    
    return [_enrich_user(u) for u in tenant_users]

@router.get("/users/{user_id}", response_model=TenantUserResponse)
async def get_tenant_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get details of a specific user in the tenant.
    
    Requires: TENANT_VIEW permission
    """
    rbac = RBACService(db)
    tenant_id = current_user["tenant_id"]
    
    rbac.require_permission(
        tenant_id=tenant_id,
        user_id=current_user["user_id"],
        permission=Permission.TENANT_VIEW
    )
    
    user = db.query(TenantUser).filter(
        TenantUser.tenant_id == tenant_id,
        TenantUser.user_id == user_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    return _enrich_user(user)

@router.put("/users/{user_id}", response_model=TenantUserResponse)
async def update_tenant_user(
    user_id: str,
    user_update: TenantUserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a user's details.
    
    Requires: TENANT_MANAGE_USERS permission
    """
    rbac = RBACService(db)
    tenant_id = current_user["tenant_id"]
    
    rbac.require_permission(
        tenant_id=tenant_id,
        user_id=current_user["user_id"],
        permission=Permission.TENANT_MANAGE_USERS
    )
    
    user = db.query(TenantUser).filter(
        TenantUser.tenant_id == tenant_id,
        TenantUser.user_id == user_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    if user_update.role_id is not None:
        # Validate role
        role = db.query(TenantRole).filter(
            TenantRole.id == user_update.role_id,
            TenantRole.tenant_id == tenant_id
        ).first()
        if not role:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id"
            )
        user.tenant_role_id = user_update.role_id
        
    db.commit()
    db.refresh(user)
    
    return _enrich_user(user)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Remove a user from the tenant.
    
    Requires: TENANT_MANAGE_USERS permission
    """
    rbac = RBACService(db)
    tenant_id = current_user["tenant_id"]
    
    rbac.require_permission(
        tenant_id=tenant_id,
        user_id=current_user["user_id"],
        permission=Permission.TENANT_MANAGE_USERS
    )
    
    # Prevent deleting oneself
    if user_id == current_user["user_id"]:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    user = db.query(TenantUser).filter(
        TenantUser.tenant_id == tenant_id,
        TenantUser.user_id == user_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()

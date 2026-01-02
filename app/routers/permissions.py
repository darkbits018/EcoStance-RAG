"""
Permission Management API endpoints.
Provides information about available permissions and permission categories.
"""

from typing import List, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.auth.rbac import RBACService
from app.auth.permissions import Permission
from app.models.tenant_user import TenantUser

from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/tenant", tags=["Permissions"])


@router.get("/permissions")
async def list_available_permissions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all available permissions that can be assigned to tenant roles.
    
    Requires: TENANT_VIEW permission
    """
    rbac = RBACService(db)
    
    # Check permission
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.TENANT_VIEW
    )
    
    # Get user's permissions to filter what they can assign
    user_permissions = rbac.get_user_permissions(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    # Only show permissions the user can assign (permissions they have)
    assignable_permissions = []
    for permission in Permission:
        # Skip admin permissions for non-super-admins
        if permission.value.startswith("admin:") and permission not in user_permissions:
            continue
        
        assignable_permissions.append({
            "name": permission.value,
            "description": _get_permission_description(permission),
            "category": _get_permission_category(permission),
            "can_assign": permission in user_permissions
        })
    
    return {
        "permissions": assignable_permissions,
        "total": len(assignable_permissions)
    }


@router.get("/permissions/categories")
async def list_permission_categories(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List permissions grouped by category for easier management.
    
    Requires: TENANT_VIEW permission
    """
    rbac = RBACService(db)
    
    # Check permission
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.TENANT_VIEW
    )
    
    # Get user's permissions to filter what they can assign
    user_permissions = rbac.get_user_permissions(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    categories = {}
    
    for permission in Permission:
        # Skip admin permissions for non-super-admins
        if permission.value.startswith("admin:") and permission not in user_permissions:
            continue
        
        category = _get_permission_category(permission)
        
        if category not in categories:
            categories[category] = {
                "name": category,
                "description": _get_category_description(category),
                "permissions": []
            }
        
        categories[category]["permissions"].append({
            "name": permission.value,
            "description": _get_permission_description(permission),
            "can_assign": permission in user_permissions
        })
    
    return {
        "categories": list(categories.values()),
        "total_categories": len(categories)
    }


@router.get("/debug/current-user")
async def debug_current_user(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Debug endpoint to see current user information and permissions.
    """
    try:
        # Log the request for debugging
        print(f"DEBUG: Current user request - User ID: {current_user.get('user_id')}, Tenant ID: {current_user.get('tenant_id')}")
        
        rbac = RBACService(db)
        
        # Get user's permissions
        user_permissions = rbac.get_user_permissions(
            tenant_id=current_user["tenant_id"],
            user_id=current_user["user_id"]
        )
        
        # Get user's role information
        tenant_user = db.query(TenantUser).filter(
            TenantUser.tenant_id == current_user["tenant_id"],
            TenantUser.user_id == current_user["user_id"]
        ).first()
        
        print(f"DEBUG: TenantUser found: {tenant_user is not None}")
        if tenant_user:
            print(f"DEBUG: System role: {tenant_user.system_role}, Legacy role: {tenant_user.role}")
        
        role_info = {}
        if tenant_user:
            if tenant_user.system_role:
                role_info = {
                    "type": "system_role",
                    "role": tenant_user.system_role,
                    "role_name": tenant_user.system_role.replace("_", " ").title()
                }
            elif tenant_user.tenant_role:
                role_info = {
                    "type": "tenant_role",
                    "role_id": tenant_user.tenant_role.id,
                    "role_name": tenant_user.tenant_role.name,
                    "role_description": tenant_user.tenant_role.description
                }
            elif tenant_user.role:
                role_info = {
                    "type": "legacy_role",
                    "role": tenant_user.role,
                    "role_name": tenant_user.role.replace("_", " ").title()
                }
        
        has_tenant_view = any(p.value == "tenant:view" for p in user_permissions)
        has_tenant_manage_users = any(p.value == "tenant:manage_users" for p in user_permissions)
        
        print(f"DEBUG: Has TENANT_VIEW: {has_tenant_view}, Has MANAGE_USERS: {has_tenant_manage_users}")
        
        return {
            "debug": True,
            "current_user": current_user,
            "tenant_user_found": tenant_user is not None,
            "tenant_user_data": tenant_user.to_dict() if tenant_user else None,
            "role_info": role_info,
            "permissions": [p.value for p in user_permissions],
            "total_permissions": len(user_permissions),
            "has_tenant_view": has_tenant_view,
            "has_tenant_manage_users": has_tenant_manage_users
        }
    
    except Exception as e:
        print(f"DEBUG: Error in debug endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "debug": True,
            "error": str(e),
            "current_user": current_user
        }


@router.get("/permissions/my-permissions")
async def get_my_permissions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the current user's permissions and role information.
    """
    rbac = RBACService(db)
    
    # Get user's permissions
    user_permissions = rbac.get_user_permissions(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    # Get user's role information
    tenant_user = db.query(TenantUser).filter(
        TenantUser.tenant_id == current_user["tenant_id"],
        TenantUser.user_id == current_user["user_id"]
    ).first()
    
    role_info = {}
    if tenant_user:
        if tenant_user.system_role:
            role_info = {
                "type": "system_role",
                "role": tenant_user.system_role,
                "role_name": tenant_user.system_role.replace("_", " ").title()
            }
        elif tenant_user.tenant_role:
            role_info = {
                "type": "tenant_role",
                "role_id": tenant_user.tenant_role.id,
                "role_name": tenant_user.tenant_role.name,
                "role_description": tenant_user.tenant_role.description
            }
        elif tenant_user.role:
            role_info = {
                "type": "legacy_role",
                "role": tenant_user.role,
                "role_name": tenant_user.role.replace("_", " ").title()
            }
    
    return {
        "user_id": current_user["user_id"],
        "tenant_id": current_user["tenant_id"],
        "role_info": role_info,
        "permissions": [p.value for p in user_permissions],
        "total_permissions": len(user_permissions)
    }


def _get_permission_category(permission: Permission) -> str:
    """Get the category for a permission based on its prefix."""
    prefix = permission.value.split(":")[0]
    
    category_map = {
        "kb": "Knowledge Base",
        "db": "Database",
        "file": "File Management",
        "tenant": "Tenant Management",
        "gmail": "Gmail Integration",
        "admin": "System Administration"
    }
    
    return category_map.get(prefix, "Other")


def _get_category_description(category: str) -> str:
    """Get description for a permission category."""
    descriptions = {
        "Knowledge Base": "Permissions for managing knowledge base content and queries",
        "Database": "Permissions for database connections and operations",
        "File Management": "Permissions for file upload, download, and management",
        "Tenant Management": "Permissions for managing tenant settings and users",
        "Gmail Integration": "Permissions for Gmail configuration and operations",
        "System Administration": "System-level administrative permissions",
        "Other": "Miscellaneous permissions"
    }
    
    return descriptions.get(category, "")


def _get_permission_description(permission: Permission) -> str:
    """Get human-readable description for a permission."""
    descriptions = {
        # Knowledge Base
        Permission.KB_VIEW: "View knowledge base content",
        Permission.KB_CREATE: "Create new knowledge base entries",
        Permission.KB_UPDATE: "Update existing knowledge base entries",
        Permission.KB_DELETE: "Delete knowledge base entries",
        Permission.KB_UPLOAD: "Upload files to knowledge base",
        Permission.KB_QUERY: "Query knowledge base content",
        
        # Database
        Permission.DB_VIEW: "View database connections and schemas",
        Permission.DB_CONNECT: "Connect to databases",
        Permission.DB_QUERY: "Execute read-only database queries",
        Permission.DB_EXECUTE: "Execute database operations",
        Permission.DB_MANAGE: "Manage database connections and settings",
        
        # File Management
        Permission.FILE_VIEW: "View file listings",
        Permission.FILE_UPLOAD: "Upload files",
        Permission.FILE_DOWNLOAD: "Download files",
        Permission.FILE_DELETE: "Delete files",
        
        # Tenant Management
        Permission.TENANT_VIEW: "View tenant information",
        Permission.TENANT_UPDATE: "Update tenant settings",
        Permission.TENANT_MANAGE_USERS: "Manage tenant users and roles",
        Permission.TENANT_MANAGE_SETTINGS: "Manage tenant configuration",
        
        # Gmail Integration
        Permission.GMAIL_VIEW: "View Gmail configuration",
        Permission.GMAIL_CONFIGURE: "Configure Gmail OAuth and settings",
        Permission.GMAIL_MANAGE_RECIPIENTS: "Manage Gmail recipients",
        Permission.GMAIL_MANAGE_SCHEDULES: "Manage Gmail sync schedules",
        Permission.GMAIL_EXECUTE_SYNC: "Execute Gmail synchronization",
        Permission.GMAIL_VIEW_LOGS: "View Gmail operation logs",
        Permission.GMAIL_SEARCH: "Search Gmail data in RAG system",
        Permission.GMAIL_ADMIN: "Full Gmail administration",
        
        # System Administration
        Permission.ADMIN_VIEW_ALL: "View all system information",
        Permission.ADMIN_MANAGE_TENANTS: "Manage all tenants",
        Permission.ADMIN_MANAGE_USERS: "Manage all users across tenants",
        Permission.ADMIN_VIEW_METRICS: "View system metrics and analytics",
        Permission.ADMIN_MANAGE_QUOTAS: "Manage tenant quotas and limits"
    }
    
    return descriptions.get(permission, permission.value)
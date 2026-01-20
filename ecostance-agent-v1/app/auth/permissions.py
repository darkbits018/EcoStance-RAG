"""
Permission constants and definitions for RBAC system.
"""

from enum import Enum
from typing import Set


class Permission(str, Enum):
    """Permission constants for tenant operations."""
    
    # Knowledge Base permissions
    KB_VIEW = "kb:view"
    KB_CREATE = "kb:create"
    KB_UPDATE = "kb:update"
    KB_DELETE = "kb:delete"
    KB_UPLOAD = "kb:upload"
    KB_QUERY = "kb:query"
    
    # Database permissions
    DB_VIEW = "db:view"
    DB_CONNECT = "db:connect"
    DB_QUERY = "db:query"
    DB_EXECUTE = "db:execute"
    DB_MANAGE = "db:manage"
    
    # File permissions
    FILE_VIEW = "file:view"
    FILE_UPLOAD = "file:upload"
    FILE_DOWNLOAD = "file:download"
    FILE_DELETE = "file:delete"
    
    # Tenant permissions
    TENANT_VIEW = "tenant:view"
    TENANT_UPDATE = "tenant:update"
    TENANT_MANAGE_USERS = "tenant:manage_users"
    TENANT_MANAGE_SETTINGS = "tenant:manage_settings"
    
    # Gmail permissions
    GMAIL_VIEW = "gmail:view"
    GMAIL_CONFIGURE = "gmail:configure"
    GMAIL_MANAGE_RECIPIENTS = "gmail:manage_recipients"
    GMAIL_MANAGE_SCHEDULES = "gmail:manage_schedules"
    GMAIL_EXECUTE_SYNC = "gmail:execute_sync"
    GMAIL_VIEW_LOGS = "gmail:view_logs"
    GMAIL_SEARCH = "gmail:search"
    GMAIL_ADMIN = "gmail:admin"

    # Dynamics permissions
    DYNAMICS_CONFIGURE = "dynamics:configure"
    DYNAMICS_SYNC = "dynamics:sync"

    # Custom CRM permissions
    CUSTOM_CRM_VIEW = "custom_crm:view"
    CUSTOM_CRM_SYNC = "custom_crm:sync"

    
    # Admin permissions
    ADMIN_VIEW_ALL = "admin:view_all"
    ADMIN_MANAGE_TENANTS = "admin:manage_tenants"
    ADMIN_MANAGE_USERS = "admin:manage_users"
    ADMIN_VIEW_METRICS = "admin:view_metrics"
    ADMIN_MANAGE_QUOTAS = "admin:manage_quotas"


class SystemRole(str, Enum):
    """System-level roles (fixed)."""
    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "tenant_admin"


class Role(str, Enum):
    """Legacy role definitions - kept for backward compatibility."""
    
    VIEWER = "viewer"
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# System role permissions (fixed)
SYSTEM_ROLE_PERMISSIONS = {
    SystemRole.SUPER_ADMIN: set(Permission),  # All permissions across all tenants
    SystemRole.TENANT_ADMIN: {
        # All tenant-scoped permissions (everything except admin:* permissions)
        Permission.KB_VIEW, Permission.KB_CREATE, Permission.KB_UPDATE, Permission.KB_DELETE,
        Permission.KB_UPLOAD, Permission.KB_QUERY,
        Permission.DB_VIEW, Permission.DB_CONNECT, Permission.DB_QUERY, 
        Permission.DB_EXECUTE, Permission.DB_MANAGE,
        Permission.FILE_VIEW, Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD, Permission.FILE_DELETE,
        Permission.TENANT_VIEW, Permission.TENANT_UPDATE, Permission.TENANT_MANAGE_USERS,
        Permission.TENANT_MANAGE_SETTINGS,
        # Gmail permissions
        Permission.GMAIL_VIEW, Permission.GMAIL_CONFIGURE, Permission.GMAIL_MANAGE_RECIPIENTS,
        Permission.GMAIL_MANAGE_SCHEDULES, Permission.GMAIL_EXECUTE_SYNC, 
        Permission.GMAIL_VIEW_LOGS, Permission.GMAIL_SEARCH, Permission.GMAIL_ADMIN,
        # Dynamics permissions
        Permission.DYNAMICS_CONFIGURE, Permission.DYNAMICS_SYNC,
        # Custom CRM permissions
        Permission.CUSTOM_CRM_VIEW, Permission.CUSTOM_CRM_SYNC
    }

}


# Legacy role to permissions mapping (kept for backward compatibility)
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.VIEWER: {
        Permission.KB_VIEW,
        Permission.KB_QUERY,
        Permission.DB_VIEW,
        Permission.FILE_VIEW,
        Permission.TENANT_VIEW,
        Permission.GMAIL_VIEW,
    },
    Role.USER: {
        Permission.KB_VIEW,
        Permission.KB_QUERY,
        Permission.KB_UPLOAD,
        Permission.DB_VIEW,
        Permission.DB_CONNECT,
        Permission.DB_QUERY,
        Permission.FILE_VIEW,
        Permission.FILE_UPLOAD,
        Permission.FILE_DOWNLOAD,
        Permission.TENANT_VIEW,
        Permission.GMAIL_VIEW,
        Permission.GMAIL_SEARCH,
    },
    Role.MANAGER: {
        Permission.KB_VIEW,
        Permission.KB_CREATE,
        Permission.KB_UPDATE,
        Permission.KB_DELETE,
        Permission.KB_UPLOAD,
        Permission.KB_QUERY,
        Permission.DB_VIEW,
        Permission.DB_CONNECT,
        Permission.DB_QUERY,
        Permission.DB_EXECUTE,
        Permission.DB_MANAGE,
        Permission.FILE_VIEW,
        Permission.FILE_UPLOAD,
        Permission.FILE_DOWNLOAD,
        Permission.FILE_DELETE,
        Permission.TENANT_VIEW,
        Permission.TENANT_UPDATE,
        Permission.TENANT_MANAGE_USERS,
        Permission.GMAIL_VIEW,
        Permission.GMAIL_MANAGE_RECIPIENTS,
        Permission.GMAIL_MANAGE_SCHEDULES,
        Permission.GMAIL_EXECUTE_SYNC,
        Permission.GMAIL_VIEW_LOGS,
        Permission.GMAIL_SEARCH,
    },
    Role.ADMIN: {
        Permission.KB_VIEW,
        Permission.KB_CREATE,
        Permission.KB_UPDATE,
        Permission.KB_DELETE,
        Permission.KB_UPLOAD,
        Permission.KB_QUERY,
        Permission.DB_VIEW,
        Permission.DB_CONNECT,
        Permission.DB_QUERY,
        Permission.DB_EXECUTE,
        Permission.DB_MANAGE,
        Permission.FILE_VIEW,
        Permission.FILE_UPLOAD,
        Permission.FILE_DOWNLOAD,
        Permission.FILE_DELETE,
        Permission.TENANT_VIEW,
        Permission.TENANT_UPDATE,
        Permission.TENANT_MANAGE_USERS,
        Permission.TENANT_MANAGE_SETTINGS,
        Permission.GMAIL_VIEW,
        Permission.GMAIL_CONFIGURE,
        Permission.GMAIL_MANAGE_RECIPIENTS,
        Permission.GMAIL_MANAGE_SCHEDULES,
        Permission.GMAIL_EXECUTE_SYNC,
        Permission.GMAIL_VIEW_LOGS,
        Permission.GMAIL_SEARCH,
        Permission.GMAIL_ADMIN,
        Permission.DYNAMICS_CONFIGURE,
        Permission.DYNAMICS_SYNC,
        Permission.CUSTOM_CRM_VIEW,
        Permission.CUSTOM_CRM_SYNC,
    },
    Role.SUPER_ADMIN: set(Permission),  # All permissions
}


def get_system_role_permissions(role: SystemRole) -> Set[Permission]:
    """Get all permissions for a given system role."""
    return SYSTEM_ROLE_PERMISSIONS.get(role, set())


def get_role_permissions(role: Role) -> Set[Permission]:
    """Get all permissions for a given role."""
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: Role, permission: Permission) -> bool:
    """Check if a role has a specific permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())

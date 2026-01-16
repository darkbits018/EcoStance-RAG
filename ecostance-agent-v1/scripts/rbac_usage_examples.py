#!/usr/bin/env python3
"""
Usage examples for the Better RBAC system.
Demonstrates how to use the new two-tier role architecture.
"""

import sys
import os
from typing import List

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.auth.rbac import RBACService
from app.auth.permissions import Permission, SystemRole
from app.models.tenant_user import TenantUser
from app.models.tenant_role import TenantRole


def example_create_custom_roles(db: Session, tenant_id: str, admin_user_id: str):
    """
    Example: Create custom tenant roles with specific permissions.
    """
    print("=== Creating Custom Tenant Roles ===")
    
    rbac = RBACService(db)
    
    # Example 1: Create a "Content Manager" role
    content_manager_permissions = [
        Permission.KB_VIEW, Permission.KB_CREATE, Permission.KB_UPDATE, Permission.KB_DELETE,
        Permission.KB_UPLOAD, Permission.KB_QUERY,
        Permission.FILE_VIEW, Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD, Permission.FILE_DELETE
    ]
    
    try:
        content_role = rbac.create_tenant_role(
            tenant_id=tenant_id,
            creator_id=admin_user_id,
            name="Content Manager",
            permissions=content_manager_permissions,
            description="Manages knowledge base content and files"
        )
        print(f"✅ Created role: {content_role.name} with {len(content_role.permissions)} permissions")
    except Exception as e:
        print(f"❌ Failed to create Content Manager role: {e}")
    
    # Example 2: Create a "Database Analyst" role
    db_analyst_permissions = [
        Permission.DB_VIEW, Permission.DB_CONNECT, Permission.DB_QUERY,
        Permission.TENANT_VIEW
    ]
    
    try:
        db_role = rbac.create_tenant_role(
            tenant_id=tenant_id,
            creator_id=admin_user_id,
            name="Database Analyst",
            permissions=db_analyst_permissions,
            description="Analyzes data with read-only database access"
        )
        print(f"✅ Created role: {db_role.name} with {len(db_role.permissions)} permissions")
    except Exception as e:
        print(f"❌ Failed to create Database Analyst role: {e}")
    
    # Example 3: Create a "Gmail Administrator" role
    gmail_admin_permissions = [
        Permission.GMAIL_VIEW, Permission.GMAIL_CONFIGURE, Permission.GMAIL_MANAGE_RECIPIENTS,
        Permission.GMAIL_MANAGE_SCHEDULES, Permission.GMAIL_EXECUTE_SYNC,
        Permission.GMAIL_VIEW_LOGS, Permission.GMAIL_SEARCH, Permission.GMAIL_ADMIN
    ]
    
    try:
        gmail_role = rbac.create_tenant_role(
            tenant_id=tenant_id,
            creator_id=admin_user_id,
            name="Gmail Administrator",
            permissions=gmail_admin_permissions,
            description="Full Gmail integration management"
        )
        print(f"✅ Created role: {gmail_role.name} with {len(gmail_role.permissions)} permissions")
    except Exception as e:
        print(f"❌ Failed to create Gmail Administrator role: {e}")


def example_assign_roles(db: Session, tenant_id: str, admin_user_id: str):
    """
    Example: Assign roles to users.
    """
    print("\n=== Assigning Roles to Users ===")
    
    rbac = RBACService(db)
    
    # Get available roles
    try:
        roles = rbac.list_tenant_roles(tenant_id, admin_user_id)
        print(f"Available roles in tenant: {[role.name for role in roles]}")
        
        if roles:
            # Example: Assign first role to a user (you'd use real user IDs)
            example_user_id = "example-user-123"
            first_role = roles[0]
            
            # Note: In practice, you'd need to ensure the user exists in the tenant
            print(f"Would assign role '{first_role.name}' to user {example_user_id}")
            # rbac.assign_tenant_role(tenant_id, example_user_id, first_role.id, admin_user_id)
        
    except Exception as e:
        print(f"❌ Failed to list or assign roles: {e}")


def example_check_permissions(db: Session, tenant_id: str, user_id: str):
    """
    Example: Check user permissions.
    """
    print(f"\n=== Checking Permissions for User {user_id} ===")
    
    rbac = RBACService(db)
    
    try:
        # Get all user permissions
        user_permissions = rbac.get_user_permissions(tenant_id, user_id)
        print(f"User has {len(user_permissions)} permissions:")
        
        for permission in sorted(user_permissions, key=lambda p: p.value):
            print(f"  ✓ {permission.value}")
        
        # Check specific permissions
        test_permissions = [
            Permission.KB_VIEW,
            Permission.DB_EXECUTE,
            Permission.TENANT_MANAGE_USERS,
            Permission.GMAIL_CONFIGURE,
            Permission.ADMIN_VIEW_ALL
        ]
        
        print(f"\nPermission checks:")
        for permission in test_permissions:
            has_permission = rbac.check_permission(tenant_id, user_id, permission)
            status = "✅" if has_permission else "❌"
            print(f"  {status} {permission.value}")
    
    except Exception as e:
        print(f"❌ Failed to check permissions: {e}")


def example_system_role_assignment(db: Session, tenant_id: str, super_admin_id: str):
    """
    Example: Assign system roles (Super Admin only).
    """
    print(f"\n=== System Role Assignment (Super Admin Only) ===")
    
    rbac = RBACService(db)
    
    try:
        # Example: Promote a user to tenant admin
        example_user_id = "user-to-promote-123"
        
        print(f"Would promote user {example_user_id} to tenant admin")
        # rbac.assign_system_role(tenant_id, example_user_id, SystemRole.TENANT_ADMIN, super_admin_id)
        
        print("Note: Only super admins can assign system roles")
    
    except Exception as e:
        print(f"❌ Failed system role assignment: {e}")


def example_role_management(db: Session, tenant_id: str, admin_user_id: str):
    """
    Example: Update and manage existing roles.
    """
    print(f"\n=== Role Management ===")
    
    rbac = RBACService(db)
    
    try:
        # List existing roles
        roles = rbac.list_tenant_roles(tenant_id, admin_user_id)
        
        if roles:
            # Example: Update the first role
            role_to_update = roles[0]
            print(f"Updating role: {role_to_update.name}")
            
            # Add a new permission
            updated_permissions = list(role_to_update.permissions)
            if Permission.TENANT_VIEW.value not in updated_permissions:
                updated_permissions.append(Permission.TENANT_VIEW.value)
            
            updated_role = rbac.update_tenant_role(
                role_id=role_to_update.id,
                updater_id=admin_user_id,
                permissions=[Permission(p) for p in updated_permissions],
                description=f"{role_to_update.description} (Updated)"
            )
            
            print(f"✅ Updated role: {updated_role.name}")
            print(f"   New permission count: {len(updated_role.permissions)}")
        
    except Exception as e:
        print(f"❌ Failed role management: {e}")


def main():
    """
    Run RBAC usage examples.
    """
    print("Better RBAC System - Usage Examples")
    print("=" * 50)
    
    # Use a test tenant and admin user
    # In practice, these would come from your authentication system
    test_tenant_id = "platform-admin-tenant-id"  # Use the migrated tenant
    test_admin_id = "super-admin-user-id"  # Use the migrated super admin
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if the test tenant and user exist
        admin_user = db.query(TenantUser).filter(
            TenantUser.tenant_id == test_tenant_id,
            TenantUser.user_id == test_admin_id
        ).first()
        
        if not admin_user:
            print("❌ Test admin user not found. Run the migration first.")
            return
        
        print(f"Using tenant: {test_tenant_id}")
        print(f"Using admin user: {test_admin_id}")
        print(f"Admin role: {admin_user.system_role or admin_user.role}")
        
        # Run examples
        example_create_custom_roles(db, test_tenant_id, test_admin_id)
        example_assign_roles(db, test_tenant_id, test_admin_id)
        example_check_permissions(db, test_tenant_id, test_admin_id)
        example_system_role_assignment(db, test_tenant_id, test_admin_id)
        example_role_management(db, test_tenant_id, test_admin_id)
        
        print(f"\n{'='*50}")
        print("✅ RBAC examples completed successfully!")
        print("\nNext steps:")
        print("1. Integrate JWT authentication with the get_current_user_info() function")
        print("2. Test the API endpoints with real authentication")
        print("3. Create a frontend interface for role management")
        print("4. Set up proper error handling and logging")
    
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
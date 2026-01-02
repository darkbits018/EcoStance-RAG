#!/usr/bin/env python3
"""
Data migration script for Better RBAC Phase 1.
Creates default tenant roles and migrates existing user roles.
"""

import sys
import os
import uuid
from datetime import datetime
from typing import Dict, List

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import Tenant, TenantUser, TenantRole
from app.auth.permissions import Permission, Role, SystemRole


def get_database_url():
    """Get database URL from environment."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    return database_url


def create_default_tenant_roles(session, tenant_id: str, admin_user_id: str) -> Dict[str, str]:
    """
    Create default tenant roles for a tenant.
    
    Returns:
        Dict mapping role names to role IDs
    """
    default_roles = {
        "Viewer": {
            "description": "Can view data and basic information",
            "permissions": [
                Permission.KB_VIEW, Permission.KB_QUERY,
                Permission.DB_VIEW, Permission.FILE_VIEW,
                Permission.TENANT_VIEW, Permission.GMAIL_VIEW
            ]
        },
        "User": {
            "description": "Standard user with basic operational permissions",
            "permissions": [
                Permission.KB_VIEW, Permission.KB_QUERY, Permission.KB_UPLOAD,
                Permission.DB_VIEW, Permission.DB_CONNECT, Permission.DB_QUERY,
                Permission.FILE_VIEW, Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD,
                Permission.TENANT_VIEW, Permission.GMAIL_VIEW, Permission.GMAIL_SEARCH
            ]
        },
        "Manager": {
            "description": "Manager with extended permissions for team management",
            "permissions": [
                Permission.KB_VIEW, Permission.KB_CREATE, Permission.KB_UPDATE, 
                Permission.KB_DELETE, Permission.KB_UPLOAD, Permission.KB_QUERY,
                Permission.DB_VIEW, Permission.DB_CONNECT, Permission.DB_QUERY, 
                Permission.DB_EXECUTE, Permission.DB_MANAGE,
                Permission.FILE_VIEW, Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD, 
                Permission.FILE_DELETE, Permission.TENANT_VIEW, Permission.TENANT_UPDATE,
                Permission.TENANT_MANAGE_USERS, Permission.GMAIL_VIEW, 
                Permission.GMAIL_MANAGE_RECIPIENTS, Permission.GMAIL_MANAGE_SCHEDULES,
                Permission.GMAIL_EXECUTE_SYNC, Permission.GMAIL_VIEW_LOGS, Permission.GMAIL_SEARCH
            ]
        },
        "Gmail Administrator": {
            "description": "Full Gmail system administration",
            "permissions": [
                Permission.GMAIL_VIEW, Permission.GMAIL_CONFIGURE, Permission.GMAIL_MANAGE_RECIPIENTS,
                Permission.GMAIL_MANAGE_SCHEDULES, Permission.GMAIL_EXECUTE_SYNC,
                Permission.GMAIL_VIEW_LOGS, Permission.GMAIL_SEARCH, Permission.GMAIL_ADMIN
            ]
        }
    }
    
    created_roles = {}
    
    for role_name, role_config in default_roles.items():
        # Check if role already exists
        existing_role = session.query(TenantRole).filter(
            TenantRole.tenant_id == tenant_id,
            TenantRole.name == role_name
        ).first()
        
        if existing_role:
            created_roles[role_name] = existing_role.id
            print(f"  Role '{role_name}' already exists")
            continue
        
        # Create the role
        tenant_role = TenantRole(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name=role_name,
            description=role_config["description"],
            permissions=[p.value for p in role_config["permissions"]],
            created_by=admin_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(tenant_role)
        created_roles[role_name] = tenant_role.id
        print(f"  Created role '{role_name}' with {len(role_config['permissions'])} permissions")
    
    return created_roles


def migrate_user_roles(session, tenant_id: str, role_mapping: Dict[str, str]):
    """
    Migrate existing user roles to the new system.
    """
    # Get all users in the tenant
    tenant_users = session.query(TenantUser).filter(
        TenantUser.tenant_id == tenant_id
    ).all()
    
    migration_stats = {
        "total_users": len(tenant_users),
        "migrated": 0,
        "tenant_admins": 0,
        "super_admins": 0,
        "skipped": 0
    }
    
    for user in tenant_users:
        if not user.role:
            migration_stats["skipped"] += 1
            continue
        
        # Handle system roles
        if user.role == "super_admin":
            user.system_role = SystemRole.SUPER_ADMIN.value
            user.tenant_role_id = None
            migration_stats["super_admins"] += 1
            print(f"    Migrated user {user.user_id} to super_admin system role")
        
        elif user.role == "admin":
            user.system_role = SystemRole.TENANT_ADMIN.value
            user.tenant_role_id = None
            migration_stats["tenant_admins"] += 1
            print(f"    Migrated user {user.user_id} to tenant_admin system role")
        
        # Handle tenant roles
        elif user.role in ["viewer", "user", "manager"]:
            role_name_mapping = {
                "viewer": "Viewer",
                "user": "User", 
                "manager": "Manager"
            }
            
            target_role_name = role_name_mapping[user.role]
            if target_role_name in role_mapping:
                user.tenant_role_id = role_mapping[target_role_name]
                user.system_role = None
                migration_stats["migrated"] += 1
                print(f"    Migrated user {user.user_id} from '{user.role}' to '{target_role_name}' tenant role")
            else:
                migration_stats["skipped"] += 1
                print(f"    Skipped user {user.user_id} - target role '{target_role_name}' not found")
        
        else:
            migration_stats["skipped"] += 1
            print(f"    Skipped user {user.user_id} - unknown role '{user.role}'")
    
    return migration_stats


def main():
    """Main migration function."""
    print("Starting Better RBAC Phase 1 data migration...")
    
    # Create database connection
    database_url = get_database_url()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Get all tenants
        tenants = session.query(Tenant).all()
        print(f"Found {len(tenants)} tenants to migrate")
        
        total_stats = {
            "tenants_processed": 0,
            "roles_created": 0,
            "users_migrated": 0,
            "tenant_admins_created": 0,
            "super_admins_created": 0
        }
        
        for tenant in tenants:
            print(f"\nProcessing tenant: {tenant.name} ({tenant.id})")
            
            # Find an admin user to use as creator for default roles
            admin_user = session.query(TenantUser).filter(
                TenantUser.tenant_id == tenant.id,
                TenantUser.role.in_(["admin", "super_admin"])
            ).first()
            
            if not admin_user:
                # If no admin user, use the first user
                admin_user = session.query(TenantUser).filter(
                    TenantUser.tenant_id == tenant.id
                ).first()
            
            if not admin_user:
                print(f"  No users found in tenant {tenant.name}, skipping...")
                continue
            
            # Create default tenant roles
            print("  Creating default tenant roles...")
            role_mapping = create_default_tenant_roles(session, tenant.id, admin_user.id)
            total_stats["roles_created"] += len(role_mapping)
            
            # Migrate existing user roles
            print("  Migrating user roles...")
            migration_stats = migrate_user_roles(session, tenant.id, role_mapping)
            
            total_stats["tenants_processed"] += 1
            total_stats["users_migrated"] += migration_stats["migrated"]
            total_stats["tenant_admins_created"] += migration_stats["tenant_admins"]
            total_stats["super_admins_created"] += migration_stats["super_admins"]
            
            print(f"  Migration stats for {tenant.name}:")
            print(f"    Total users: {migration_stats['total_users']}")
            print(f"    Migrated to tenant roles: {migration_stats['migrated']}")
            print(f"    Migrated to tenant_admin: {migration_stats['tenant_admins']}")
            print(f"    Migrated to super_admin: {migration_stats['super_admins']}")
            print(f"    Skipped: {migration_stats['skipped']}")
        
        # Commit all changes
        session.commit()
        
        print(f"\n=== Migration Summary ===")
        print(f"Tenants processed: {total_stats['tenants_processed']}")
        print(f"Default roles created: {total_stats['roles_created']}")
        print(f"Users migrated to tenant roles: {total_stats['users_migrated']}")
        print(f"Users migrated to tenant_admin: {total_stats['tenant_admins_created']}")
        print(f"Users migrated to super_admin: {total_stats['super_admins_created']}")
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        session.rollback()
        raise
    
    finally:
        session.close()


if __name__ == "__main__":
    main()
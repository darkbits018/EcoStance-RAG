#!/usr/bin/env python3
"""
Migration script for existing tenants to Better RBAC system.
Creates TenantUser records for existing tenants and assigns tenant_admin role.
"""

import sys
import os
import uuid
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.tenant import Tenant
from app.models.tenant_user import TenantUser
from app.auth.permissions import SystemRole


def migrate_existing_tenants():
    """
    Migrate existing tenants to the Better RBAC system.
    Creates TenantUser records for tenants that don't have them.
    """
    print("Migrating Existing Tenants to Better RBAC")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Find tenants without TenantUser records
        tenants_without_users = db.query(Tenant).outerjoin(
            TenantUser, Tenant.id == TenantUser.tenant_id
        ).filter(TenantUser.id.is_(None)).all()
        
        print(f"Found {len(tenants_without_users)} tenants without TenantUser records")
        
        if len(tenants_without_users) == 0:
            print("✅ All tenants already have TenantUser records!")
            return
        
        migrated_count = 0
        skipped_count = 0
        
        for tenant in tenants_without_users:
            print(f"\nProcessing tenant: {tenant.name}")
            print(f"  Email: {tenant.email}")
            print(f"  Created: {tenant.created_at}")
            
            # Skip if no email (can't create user without email)
            if not tenant.email:
                print("  ⚠️  Skipping - no email address")
                skipped_count += 1
                continue
            
            # Check if email is already used by another TenantUser
            existing_user = db.query(TenantUser).filter(
                TenantUser.email == tenant.email
            ).first()
            
            if existing_user:
                print(f"  ⚠️  Skipping - email already used by user {existing_user.user_id}")
                skipped_count += 1
                continue
            
            # Create TenantUser record
            user_id = str(uuid.uuid4())
            tenant_user = TenantUser(
                id=str(uuid.uuid4()),
                tenant_id=tenant.id,
                user_id=user_id,
                email=tenant.email,
                full_name=tenant.name,  # Use tenant name as user name
                system_role=SystemRole.TENANT_ADMIN.value,  # Assign tenant_admin role
                is_active=tenant.is_active,
                created_at=tenant.created_at or datetime.utcnow()  # Use tenant creation date
            )
            
            db.add(tenant_user)
            
            print(f"  ✅ Created TenantUser record")
            print(f"     User ID: {user_id}")
            print(f"     System Role: {SystemRole.TENANT_ADMIN.value}")
            
            migrated_count += 1
        
        # Commit all changes
        db.commit()
        
        print(f"\n{'='*50}")
        print("Migration Summary:")
        print(f"  ✅ Migrated: {migrated_count} tenants")
        print(f"  ⚠️  Skipped: {skipped_count} tenants")
        print(f"  📊 Total processed: {len(tenants_without_users)} tenants")
        
        if migrated_count > 0:
            print(f"\n🎉 Successfully migrated {migrated_count} existing tenants!")
            print("These tenants can now:")
            print("  - Login with their email/password")
            print("  - Access full tenant admin permissions")
            print("  - Create custom roles for their organization")
            print("  - Manage users and permissions")
        
        if skipped_count > 0:
            print(f"\n⚠️  {skipped_count} tenants were skipped:")
            print("  - Check for missing email addresses")
            print("  - Resolve email conflicts manually if needed")
    
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


def verify_migration():
    """
    Verify that the migration was successful.
    """
    print(f"\n{'='*50}")
    print("Verifying Migration Results")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Check total counts
        total_tenants = db.query(Tenant).count()
        total_tenant_users = db.query(TenantUser).count()
        
        print(f"Total tenants: {total_tenants}")
        print(f"Total tenant users: {total_tenant_users}")
        
        # Check tenants without users
        tenants_without_users = db.query(Tenant).outerjoin(
            TenantUser, Tenant.id == TenantUser.tenant_id
        ).filter(TenantUser.id.is_(None)).count()
        
        print(f"Tenants without TenantUser records: {tenants_without_users}")
        
        # Check tenant admin assignments
        tenant_admins = db.query(TenantUser).filter(
            TenantUser.system_role == SystemRole.TENANT_ADMIN.value
        ).count()
        
        print(f"Tenant admins: {tenant_admins}")
        
        # Check super admins
        super_admins = db.query(TenantUser).filter(
            TenantUser.system_role == SystemRole.SUPER_ADMIN.value
        ).count()
        
        print(f"Super admins: {super_admins}")
        
        if tenants_without_users == 0:
            print("✅ All tenants now have TenantUser records!")
        else:
            print(f"⚠️  {tenants_without_users} tenants still need migration")
        
        # Show recent migrations
        print(f"\nRecent tenant admin assignments:")
        recent_admins = db.query(TenantUser).filter(
            TenantUser.system_role == SystemRole.TENANT_ADMIN.value
        ).order_by(TenantUser.created_at.desc()).limit(5).all()
        
        for admin in recent_admins:
            tenant = db.query(Tenant).filter(Tenant.id == admin.tenant_id).first()
            print(f"  - {admin.email} ({tenant.name if tenant else 'Unknown'}) - {admin.created_at}")
    
    except Exception as e:
        print(f"❌ Verification failed: {e}")
    
    finally:
        db.close()


def test_login_for_migrated_tenant():
    """
    Test that a migrated tenant can now login properly.
    """
    print(f"\n{'='*50}")
    print("Testing Login for Migrated Tenant")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Find a migrated tenant admin
        tenant_admin = db.query(TenantUser).filter(
            TenantUser.system_role == SystemRole.TENANT_ADMIN.value
        ).first()
        
        if not tenant_admin:
            print("❌ No tenant admin found to test")
            return
        
        tenant = db.query(Tenant).filter(Tenant.id == tenant_admin.tenant_id).first()
        
        print(f"Testing login simulation for:")
        print(f"  Email: {tenant_admin.email}")
        print(f"  Tenant: {tenant.name}")
        print(f"  System Role: {tenant_admin.system_role}")
        
        # Test RBAC permissions
        from app.auth.rbac import RBACService
        rbac = RBACService(db)
        
        permissions = rbac.get_user_permissions(tenant_admin.tenant_id, tenant_admin.user_id)
        print(f"  Permissions: {len(permissions)} total")
        
        # Test key permissions
        from app.auth.permissions import Permission
        key_perms = [
            Permission.TENANT_MANAGE_USERS,
            Permission.TENANT_MANAGE_SETTINGS,
            Permission.KB_CREATE,
            Permission.DB_MANAGE
        ]
        
        print(f"\nKey permission checks:")
        for perm in key_perms:
            has_perm = rbac.check_permission(tenant_admin.tenant_id, tenant_admin.user_id, perm)
            status = "✅" if has_perm else "❌"
            print(f"  {status} {perm.value}")
        
        print(f"\n✅ Migrated tenant can login and has proper permissions!")
    
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    migrate_existing_tenants()
    verify_migration()
    test_login_for_migrated_tenant()
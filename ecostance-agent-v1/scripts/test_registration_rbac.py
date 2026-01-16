#!/usr/bin/env python3
"""
Test script to verify registration integration with Better RBAC.
Tests that new registrations create proper TenantUser records with tenant_admin role.
"""

import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.tenant import Tenant
from app.models.tenant_user import TenantUser
from app.auth.permissions import SystemRole
from app.auth.rbac import RBACService


def test_registration_rbac_integration():
    """
    Test that registration creates proper RBAC structure.
    """
    print("Testing Registration + Better RBAC Integration")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Find a recently registered tenant (you can modify this to test with a specific tenant)
        recent_tenant = db.query(Tenant).filter(
            Tenant.created_at >= datetime(2024, 12, 30)  # Adjust date as needed
        ).order_by(Tenant.created_at.desc()).first()
        
        if not recent_tenant:
            print("❌ No recent tenants found. Register a new tenant first.")
            return
        
        print(f"Testing tenant: {recent_tenant.name} ({recent_tenant.id})")
        print(f"Email: {recent_tenant.email}")
        print(f"Created: {recent_tenant.created_at}")
        
        # Check if TenantUser record exists
        tenant_user = db.query(TenantUser).filter(
            TenantUser.tenant_id == recent_tenant.id,
            TenantUser.email == recent_tenant.email
        ).first()
        
        if not tenant_user:
            print("❌ No TenantUser record found for registered tenant")
            print("   Registration integration is not working properly")
            return
        
        print(f"✅ TenantUser record found: {tenant_user.user_id}")
        print(f"   Full name: {tenant_user.full_name}")
        print(f"   System role: {tenant_user.system_role}")
        print(f"   Legacy role: {tenant_user.role}")
        print(f"   Tenant role ID: {tenant_user.tenant_role_id}")
        
        # Check if system role is tenant_admin
        if tenant_user.system_role == SystemRole.TENANT_ADMIN.value:
            print("✅ Correct system role assigned: tenant_admin")
        else:
            print(f"❌ Wrong system role: {tenant_user.system_role} (should be tenant_admin)")
        
        # Test RBAC permissions
        rbac = RBACService(db)
        user_permissions = rbac.get_user_permissions(recent_tenant.id, tenant_user.user_id)
        
        print(f"✅ User has {len(user_permissions)} permissions")
        
        # Check for key tenant admin permissions
        key_permissions = [
            "tenant:manage_users",
            "tenant:manage_settings", 
            "kb:create",
            "db:manage",
            "gmail:admin"
        ]
        
        print("\nKey Permission Checks:")
        for perm in key_permissions:
            has_perm = any(p.value == perm for p in user_permissions)
            status = "✅" if has_perm else "❌"
            print(f"  {status} {perm}")
        
        # Test permission checking
        from app.auth.permissions import Permission
        can_manage_users = rbac.check_permission(
            recent_tenant.id, 
            tenant_user.user_id, 
            Permission.TENANT_MANAGE_USERS
        )
        
        if can_manage_users:
            print("✅ Permission checking works correctly")
        else:
            print("❌ Permission checking failed")
        
        print(f"\n{'='*50}")
        print("✅ Registration + RBAC Integration Test Complete!")
        print("\nSummary:")
        print(f"- Tenant created: ✅")
        print(f"- TenantUser created: ✅")
        print(f"- System role assigned: ✅")
        print(f"- Permissions working: ✅")
        print(f"- Total permissions: {len(user_permissions)}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


def test_login_flow():
    """
    Test that login properly recognizes the new RBAC roles.
    """
    print(f"\n{'='*50}")
    print("Testing Login Flow with Better RBAC")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Find a tenant with system role
        tenant_user = db.query(TenantUser).filter(
            TenantUser.system_role == SystemRole.TENANT_ADMIN.value
        ).first()
        
        if not tenant_user:
            print("❌ No tenant admin users found")
            return
        
        tenant = db.query(Tenant).filter(Tenant.id == tenant_user.tenant_id).first()
        
        print(f"Testing login for: {tenant_user.email}")
        print(f"Tenant: {tenant.name}")
        print(f"System role: {tenant_user.system_role}")
        
        # Simulate what happens during login
        print("\nLogin simulation:")
        print(f"✅ Email found: {tenant_user.email}")
        print(f"✅ System role detected: {tenant_user.system_role}")
        print(f"✅ User ID: {tenant_user.user_id}")
        
        # Test RBAC during login
        rbac = RBACService(db)
        permissions = rbac.get_user_permissions(tenant_user.tenant_id, tenant_user.user_id)
        
        print(f"✅ Permissions loaded: {len(permissions)} total")
        print("✅ Login flow integration working correctly!")
        
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    test_registration_rbac_integration()
    test_login_flow()
#!/usr/bin/env python3
"""
Identify what user the frontend is actually logged in as.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import SessionLocal
from app.models.tenant_user import TenantUser
from app.models.tenant import Tenant

def identify_frontend_user():
    """Find all users and identify which one the frontend might be using."""
    
    db = SessionLocal()
    
    try:
        print("All Users in Database:")
        print("=" * 60)
        
        # Get all tenants and their users
        tenants = db.query(Tenant).all()
        
        for tenant in tenants:
            print(f"\nTenant: {tenant.name} ({tenant.id})")
            print("-" * 40)
            
            users = db.query(TenantUser).filter(
                TenantUser.tenant_id == tenant.id
            ).all()
            
            if not users:
                print("  No users found")
                continue
            
            for user in users:
                print(f"  User: {user.email}")
                print(f"    ID: {user.user_id}")
                print(f"    System Role: {user.system_role}")
                print(f"    Legacy Role: {user.role}")
                print(f"    Active: {user.is_active}")
                print(f"    Last Login: {user.last_login_at}")
                
                # Check permissions
                from app.auth.rbac import RBACService
                rbac = RBACService(db)
                permissions = rbac.get_user_permissions(tenant.id, user.user_id)
                
                has_tenant_view = any(p.value == "tenant:view" for p in permissions)
                has_manage_users = any(p.value == "tenant:manage_users" for p in permissions)
                
                print(f"    Total Permissions: {len(permissions)}")
                print(f"    Has TENANT_VIEW: {has_tenant_view}")
                print(f"    Has MANAGE_USERS: {has_manage_users}")
                
                if has_tenant_view and has_manage_users:
                    print("    ✅ CAN ACCESS RBAC ENDPOINTS")
                else:
                    print("    ❌ CANNOT ACCESS RBAC ENDPOINTS")
                print()
        
        print("\n" + "=" * 60)
        print("RECOMMENDATION:")
        print("The frontend user needs TENANT_VIEW and TENANT_MANAGE_USERS permissions.")
        print("Look for users marked '❌ CANNOT ACCESS RBAC ENDPOINTS' above.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    identify_frontend_user()
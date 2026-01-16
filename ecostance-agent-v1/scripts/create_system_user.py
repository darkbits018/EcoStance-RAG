#!/usr/bin/env python3
"""
Create a system user for header-based authentication.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import SessionLocal
from app.models.tenant_user import TenantUser
from app.auth.permissions import SystemRole

def create_system_user():
    """Create a system user for each tenant to support header-based auth."""
    
    db = SessionLocal()
    
    try:
        # Get all tenants that don't have a system user
        from app.models.tenant import Tenant
        
        tenants = db.query(Tenant).all()
        
        for tenant in tenants:
            # Check if system user already exists
            existing_system_user = db.query(TenantUser).filter(
                TenantUser.tenant_id == tenant.id,
                TenantUser.user_id == "system"
            ).first()
            
            if not existing_system_user:
                # Create system user with tenant_admin permissions
                system_user = TenantUser(
                    tenant_id=tenant.id,
                    user_id="system",
                    email=f"system@{tenant.id}",
                    full_name="System User",
                    system_role=SystemRole.TENANT_ADMIN.value,
                    is_active=True
                )
                
                db.add(system_user)
                print(f"✅ Created system user for tenant: {tenant.name} ({tenant.id})")
            else:
                print(f"ℹ️  System user already exists for tenant: {tenant.name}")
        
        db.commit()
        print(f"\n✅ System user creation complete!")
        
    except Exception as e:
        print(f"❌ Error creating system users: {e}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    create_system_user()
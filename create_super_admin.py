"""
Script to create a super admin user for the platform.
Run this once to create your first super admin account.
"""
import sys
import uuid
from datetime import datetime
import bcrypt
from sqlalchemy.orm import Session

from app.db.database import SessionLocal, engine
from app.models.tenant import Tenant
from app.models.tenant_user import TenantUser

def create_super_admin():
    """Create a super admin user."""
    
    print("=" * 60)
    print("CREATE SUPER ADMIN USER")
    print("=" * 60)
    print()
    
    # Get user input
    print("Enter super admin details:")
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    full_name = input("Full Name: ").strip()
    
    if not email or not password or not full_name:
        print("\n❌ Error: All fields are required!")
        return
    
    # Confirm
    print(f"\nCreating super admin:")
    print(f"  Email: {email}")
    print(f"  Name: {full_name}")
    print(f"  Role: super_admin")
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("Cancelled.")
        return
    
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(TenantUser).filter(
            TenantUser.email == email
        ).first()
        
        if existing_user:
            print(f"\n❌ Error: User with email {email} already exists!")
            return
        
        # Create a special "Platform" tenant for super admins
        platform_tenant = db.query(Tenant).filter(
            Tenant.name == "Platform Administration"
        ).first()
        
        if not platform_tenant:
            print("\nCreating Platform Administration tenant...")
            platform_tenant = Tenant(
                id=str(uuid.uuid4()),
                name="Platform Administration",
                slug="platform-admin",
                email="platform@admin.internal",
                billing_tier="enterprise",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(platform_tenant)
            db.flush()
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create super admin user
        super_admin = TenantUser(
            id=str(uuid.uuid4()),
            tenant_id=platform_tenant.id,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role="super_admin",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(super_admin)
        db.commit()
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Super admin user created!")
        print("=" * 60)
        print(f"\nLogin credentials:")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"  Role: super_admin")
        print(f"\nYou can now login at: http://localhost:8000/docs")
        print("Use POST /api/v1/auth/login with these credentials")
        print("\n⚠️  IMPORTANT: Save these credentials securely!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating super admin: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_super_admin()

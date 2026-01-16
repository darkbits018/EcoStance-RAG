"""
Debug script to check user roles and permissions.
"""
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import DATABASE_URL
from app.models.tenant_user import TenantUser
from app.auth.rbac import RBACService
from app.auth.permissions import Permission, Role, SystemRole

def check_user_role(email_to_check: str):
    print(f"Checking role for: {email_to_check}")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        user = db.query(TenantUser).filter(TenantUser.email == email_to_check).first()
        if not user:
            print("User not found!")
            return

        print(f"User ID: {user.user_id}")
        print(f"System Role: {user.system_role}")
        print(f"Legacy Role: {user.role}")
        print(f"Tenant Role ID: {user.tenant_role_id}")
        
        rbac = RBACService(db)
        permissions = rbac.get_user_permissions(user.tenant_id, user.user_id)
        
        print("\nEffective Permissions:")
        for p in permissions:
            if "dynamics" in p:
                print(f" - {p} [DYNAMICS]")
            else:
                print(f" - {p}")
                
        if Permission.DYNAMICS_CONFIGURE in permissions:
            print("\nSUCCESS: User HAS dynamics:configure permission.")
        else:
            print("\nFAILURE: User DOES NOT HAVE dynamics:configure permission.")

    finally:
        db.close()

if __name__ == "__main__":
    email = "abhaygp18.dev@gmail.com" # Replace if you logged in with different email
    check_user_role(email)

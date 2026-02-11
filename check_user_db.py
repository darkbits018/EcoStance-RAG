
import os
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_user(email, password):
    from app.models.tenant import Tenant
    from app.models.tenant_user import TenantUser
    
    db = SessionLocal()
    try:
        print(f"Checking for user: {email}")
        
        # Check Tenant
        tenant = db.query(Tenant).filter(Tenant.email == email).first()
        if tenant:
            print(f"Found Tenant: {tenant.id}")
            if tenant.password_hash:
                is_valid = bcrypt.checkpw(password.encode('utf-8'), tenant.password_hash.encode('utf-8'))
                print(f"Tenant Password Valid: {is_valid}")
            else:
                print("Tenant has no password hash")
        else:
            print("Tenant not found")
            
        # Check TenantUser
        tenant_user = db.query(TenantUser).filter(TenantUser.email == email).first()
        if tenant_user:
            print(f"Found TenantUser: {tenant_user.id} in Tenant: {tenant_user.tenant_id}")
            if tenant_user.password_hash:
                is_valid = bcrypt.checkpw(password.encode('utf-8'), tenant_user.password_hash.encode('utf-8'))
                print(f"TenantUser Password Valid: {is_valid}")
            else:
                print("TenantUser has no password hash")
        else:
            print("TenantUser not found")
            
    finally:
        db.close()

if __name__ == "__main__":
    email = "abhay.1plusbackup@gmail.com"
    password = "$G$LZUZ3S_5s2q."
    check_user(email, password)

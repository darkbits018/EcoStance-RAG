
import os
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_all_users(password):
    from app.models.tenant_user import TenantUser
    from app.models.tenant import Tenant
    
    db = SessionLocal()
    try:
        users = db.query(TenantUser).all()
        print(f"Checking {len(users)} TenantUsers...")
        for u in users:
            if u.password_hash:
                try:
                    if bcrypt.checkpw(password.encode('utf-8'), u.password_hash.encode('utf-8')):
                        print(f"MATCH FOUND (TenantUser): {u.email} (Tenant: {u.tenant_id})")
                except:
                    pass
                    
        tenants = db.query(Tenant).all()
        print(f"Checking {len(tenants)} Tenants...")
        for t in tenants:
            if t.password_hash:
                try:
                    if bcrypt.checkpw(password.encode('utf-8'), t.password_hash.encode('utf-8')):
                        print(f"MATCH FOUND (Tenant): {t.email} (ID: {t.id})")
                except:
                    pass
    finally:
        db.close()

if __name__ == "__main__":
    password = "$G$LZUZ3S_5s2q."
    check_all_users(password)
    print("\nChecking without dot...")
    check_all_users("$G$LZUZ3S_5s2q")

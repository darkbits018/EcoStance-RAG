
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def list_users():
    from app.models.tenant_user import TenantUser
    db = SessionLocal()
    try:
        users = db.query(TenantUser).all()
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f"Email: {u.email}, Role: {u.system_role}, Active: {u.is_active}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()


import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def list_tenants():
    from app.models.tenant import Tenant
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        print(f"Total Tenants: {len(tenants)}")
        for t in tenants:
            print(f"ID: {t.id}, Name: {t.name}, Email: {t.email}")
    finally:
        db.close()

if __name__ == "__main__":
    list_tenants()

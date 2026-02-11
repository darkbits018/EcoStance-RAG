
import os
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_pwd(email, password):
    from app.models.tenant_user import TenantUser
    db = SessionLocal()
    try:
        user = db.query(TenantUser).filter(TenantUser.email == email).first()
        if user:
            print(f"User: {email}")
            if user.password_hash:
                is_valid = bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))
                print(f"Password Valid: {is_valid}")
            else:
                print("No password hash")
        else:
            print("User not found")
    finally:
        db.close()

if __name__ == "__main__":
    password = "$G$LZUZ3S_5s2q."
    check_pwd("abhay@superadmin.com", password)
    check_pwd("abhaygp18.dev@gmail.com", password)
    check_pwd("abhi@ecostance.com", password)

from app.db.database import engine
from sqlalchemy import text

def check_db():
    with engine.connect() as conn:
        tables = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")).fetchall()
        print("Tables in DB:")
        for t in tables:
            print(f"- {t[0]}")
            
        print("\nChecking columns for isolation:")
        checks = [
            ("tenant_users", "gmail_config"),
            ("gmail_schedules", "user_id"),
            ("gmail_execution_logs", "user_id"),
            ("gmail_messages", "user_id")
        ]
        
        for table, col in checks:
            res = conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}' AND column_name='{col}'")).fetchone()
            if res:
                print(f"[OK] {table}.{col} exists")
            else:
                print(f"[MISSING] {table}.{col} does NOT exist")

if __name__ == "__main__":
    check_db()

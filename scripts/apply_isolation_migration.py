import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.database import engine

def apply_isolation_migration():
    print(f"Connecting to database: {engine.url}")
    with engine.connect() as conn:
        try:
            # 1. Add gmail_config to tenant_users table
            print("Checking 'gmail_config' in 'tenant_users'...")
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='tenant_users' AND column_name='gmail_config'")).fetchone()
            if not res:
                print("Adding 'gmail_config' column to 'tenant_users'...")
                conn.execute(text("ALTER TABLE tenant_users ADD COLUMN gmail_config JSON DEFAULT '{}'"))
            
            # 2. Add user_id to gmail_schedules
            print("Checking 'user_id' in 'gmail_schedules'...")
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='gmail_schedules' AND column_name='user_id'")).fetchone()
            if not res:
                print("Adding 'user_id' column to 'gmail_schedules'...")
                conn.execute(text("ALTER TABLE gmail_schedules ADD COLUMN user_id VARCHAR(36)"))
            
            # 3. Add user_id to gmail_execution_logs
            print("Checking 'user_id' in 'gmail_execution_logs'...")
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='gmail_execution_logs' AND column_name='user_id'")).fetchone()
            if not res:
                print("Adding 'user_id' column to 'gmail_execution_logs'...")
                conn.execute(text("ALTER TABLE gmail_execution_logs ADD COLUMN user_id VARCHAR(36)"))
            
            # 4. Add user_id to gmail_messages
            print("Checking 'user_id' in 'gmail_messages'...")
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='gmail_messages' AND column_name='user_id'")).fetchone()
            if not res:
                print("Adding 'user_id' column to 'gmail_messages'...")
                conn.execute(text("ALTER TABLE gmail_messages ADD COLUMN user_id VARCHAR(36)"))
            
            conn.commit()
            print("Migration completed successfully.")
        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback()

if __name__ == "__main__":
    apply_isolation_migration()

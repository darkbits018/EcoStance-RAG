import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.database import engine

def apply_recipient_isolation_migration():
    print(f"Connecting to database: {engine.url}")
    with engine.connect() as conn:
        try:
            # Add user_id to gmail_recipients
            print("Checking 'user_id' in 'gmail_recipients'...")
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='gmail_recipients' AND column_name='user_id'")).fetchone()
            if not res:
                print("Adding 'user_id' column to 'gmail_recipients'...")
                conn.execute(text("ALTER TABLE gmail_recipients ADD COLUMN user_id VARCHAR(36)"))
            
            conn.commit()
            print("Migration completed successfully.")
        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback()

if __name__ == "__main__":
    apply_recipient_isolation_migration()

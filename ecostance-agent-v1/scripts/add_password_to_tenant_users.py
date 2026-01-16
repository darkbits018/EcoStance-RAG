import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.database import engine

def add_password_column():
    print(f"Connecting to database: {engine.url}")
    with engine.connect() as conn:
        try:
            # Check if column exists first
            # Note: This information_schema query is for PostgreSQL/MySQL
            # For SQLite this might fail or return nothing, so we handle exceptions.
            column_exists = False
            try:
                result = conn.execute(text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name='tenant_users' AND column_name='password_hash'"
                ))
                if result.fetchone():
                    column_exists = True
            except Exception:
                # Likely SQLite or permissions. We can try PRAGMA for SQLite or just try adding and catch error
                pass

            if column_exists:
                print("Column 'password_hash' already exists in 'tenant_users'.")
                return

            print("Attempting to add 'password_hash' column to 'tenant_users' table...")
            conn.execute(text("ALTER TABLE tenant_users ADD COLUMN password_hash VARCHAR(255)"))
            conn.commit()
            print("Successfully added 'password_hash' column.")
            
        except Exception as e:
            print(f"Error adding column: {e}")
            if "Duplicate column" in str(e) or "already exists" in str(e):
                 print("Column seems to already exist.")

if __name__ == "__main__":
    add_password_column()

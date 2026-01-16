"""
Migration script to add 'dynamics_config' column to 'tenants' table.
And create 'dynamics_messages' table.
"""
import os
import sys

# Add parent directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.db.database import DATABASE_URL
from app.db.database import Base
from app.models.dynamics import DynamicsMessage

def run_migration():
    print(f"Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # 1. Add column to tenants
        try:
            print("Adding 'dynamics_config' column to 'tenants' table...")
            connection.execute(text("ALTER TABLE tenants ADD COLUMN dynamics_config JSON DEFAULT '{}'"))
            print("Column added successfully.")
        except Exception as e:
            if "duplicate column" in str(e):
                print("Column 'dynamics_config' already exists.")
            else:
                print(f"Error adding column: {e}")

        # 2. Add DynamicsMessage Table
        # We can use SQLAlchemy's metadata create_all for this, as it handles checks
        print("Creating 'dynamics_messages' table if not exists...")
        DynamicsMessage.__table__.create(connection, checkfirst=True)
        print("Table creation check complete.")
        
        connection.commit()
        print("Migration completed successfully.")

if __name__ == "__main__":
    run_migration()

import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.database import engine

def apply_gmail_migration():
    print(f"Connecting to database: {engine.url}")
    with engine.connect() as conn:
        try:
            # 1. Add gmail_config to tenants table
            print("Checking 'gmail_config' column in 'tenants'...")
            column_exists = False
            try:
                result = conn.execute(text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name='tenants' AND column_name='gmail_config'"
                ))
                if result.fetchone():
                    column_exists = True
            except Exception:
                pass

            if not column_exists:
                print("Adding 'gmail_config' column to 'tenants' table...")
                # Note: JSON type in Postgres is JSON or JSONB. In generic SQL or SQLite it might differ or be TEXT.
                # SQLAlchemy handles this in code, but raw SQL migration needs dialect awareness.
                # Assuming Postgres based on previous conversation:
                conn.execute(text("ALTER TABLE tenants ADD COLUMN gmail_config JSON DEFAULT '{}'"))
                print("Added 'gmail_config' column.")
            else:
                print("'gmail_config' column already exists.")

            # 2. Create gmail_recipients table
            print("Creating 'gmail_recipients' table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS gmail_recipients (
                    id VARCHAR(36) PRIMARY KEY,
                    tenant_id VARCHAR(36) NOT NULL,
                    email_address VARCHAR(255) NOT NULL,
                    display_name VARCHAR(255),
                    group_name VARCHAR(100),
                    enabled BOOLEAN DEFAULT TRUE,
                    filters JSON DEFAULT '{}',
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
                    FOREIGN KEY(tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
                )
            """))

            # 3. Create gmail_schedules table
            print("Creating 'gmail_schedules' table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS gmail_schedules (
                    id VARCHAR(36) PRIMARY KEY,
                    tenant_id VARCHAR(36) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    schedule_type VARCHAR(50) NOT NULL,
                    schedule_config JSON NOT NULL,
                    recipient_ids JSON DEFAULT '[]',
                    enabled BOOLEAN DEFAULT TRUE,
                    last_run TIMESTAMP WITHOUT TIME ZONE,
                    next_run TIMESTAMP WITHOUT TIME ZONE,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
                    FOREIGN KEY(tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
                )
            """))

            # 4. Create gmail_execution_logs table
            print("Creating 'gmail_execution_logs' table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS gmail_execution_logs (
                    id VARCHAR(36) PRIMARY KEY,
                    tenant_id VARCHAR(36) NOT NULL,
                    schedule_id VARCHAR(36),
                    recipient_id VARCHAR(36),
                    execution_type VARCHAR(50) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    emails_processed INTEGER DEFAULT 0,
                    emails_added INTEGER DEFAULT 0,
                    errors JSON,
                    start_time TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
                    end_time TIMESTAMP WITHOUT TIME ZONE,
                    duration_ms INTEGER,
                    FOREIGN KEY(tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
                    FOREIGN KEY(schedule_id) REFERENCES gmail_schedules(id) ON DELETE SET NULL,
                    FOREIGN KEY(recipient_id) REFERENCES gmail_recipients(id) ON DELETE SET NULL
                )
            """))
            
            conn.commit()
            print("Gmail migration completed successfully.")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback()

if __name__ == "__main__":
    apply_gmail_migration()

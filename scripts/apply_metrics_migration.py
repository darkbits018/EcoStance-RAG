from app.db.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_migration():
    migration_file = "migrations/006_create_metrics_tables_postgres.sql"
    with open(migration_file, "r") as f:
        sql = f.read()
    
    # Split by semicolon to execute one by one (simplified)
    # Actually, SQLAlchemy's text() context can handle multiple statements if supported by the driver/DB
    # But for safety, we often split. Postgres supports multiple statements in one execute call.
    
    with engine.connect() as conn:
        try:
            logger.info(f"Applying migration from {migration_file}...")
            # Using transaction to ensure all or nothing
            with conn.begin():
                conn.execute(text(sql))
            logger.info("✓ Migration applied successfully.")
        except Exception as e:
            logger.error(f"Error applying migration: {e}")
            raise

if __name__ == "__main__":
    apply_migration()

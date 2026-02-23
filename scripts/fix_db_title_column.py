from app.db.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upgrade_schema():
    with engine.connect() as conn:
        try:
            logger.info("Attempting to add 'title' column to public_agent_sessions...")
            conn.execute(text("ALTER TABLE public_agent_sessions ADD COLUMN title VARCHAR(255)"))
            conn.commit()
            logger.info("✓ Column 'title' added successfully.")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                logger.info("Column 'title' already exists, skipping.")
            else:
                logger.error(f"Error adding column: {e}")
                raise

if __name__ == "__main__":
    upgrade_schema()

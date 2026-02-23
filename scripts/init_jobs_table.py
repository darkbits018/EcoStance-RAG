from app.db.database import Base, engine
from app.models.background_job import BackgroundJob
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_job_table():
    logger.info("Creating background_jobs table...")
    try:
        BackgroundJob.__table__.create(bind=engine, checkfirst=True)
        logger.info("✓ background_jobs table created or already exists")
    except Exception as e:
        logger.error(f"Failed to create table: {e}")

if __name__ == "__main__":
    setup_job_table()

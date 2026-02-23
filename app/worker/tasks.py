import asyncio
import logging
from .celery_app import celery_app
from ..services.multilingual_integration_service import process_file_intelligently
from ..services.job_service import job_tracker

logger = logging.getLogger("CeleryWorker")

@celery_app.task(name="process_file_task", bind=True)
def process_file_task(self, job_id: str, file_path: str, collection_name: str, tenant_id: str):
    """
    Celery task to process a file and upload to Qdrant.
    This runs in a separate worker process.
    """
    logger.info(f"Starting Celery task for job {job_id}, file: {file_path}")
    
    # We need to run the async processing function in a synchronous Celery worker
    try:
        # Update job status to processing
        job_tracker.start_job(job_id)
        
        # Run the async pipeline
        # Use asyncio.run for a fresh event loop in the worker thread/process
        asyncio.run(process_file_intelligently(
            file_path=file_path,
            collection_name=collection_name,
            tenant_id=tenant_id,
            job_id=job_id
        ))
        
        logger.info(f"✓ Celery task completed for job {job_id}")
        return {"status": "completed", "job_id": job_id}
        
    except Exception as e:
        logger.error(f"Celery task failed for job {job_id}: {e}")
        job_tracker.fail_job(job_id, str(e))
        return {"status": "failed", "job_id": job_id, "error": str(e)}

"""
Check the status of a specific processing job.
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.job_service import job_tracker

def check_job(job_id):
    # Depending on how job_tracker is implemented (in-memory vs redis), 
    # we might need to be running in the same process. 
    # If it's in-memory, this script WON'T find it because it's a separate process.
    # But let's check if it persists to disk or DB.
    
    print(f"Checking job: {job_id}")
    job = job_tracker.get_job_dict(job_id)
    if job:
        print(f"Job Found: {job}")
    else:
        print("Job NOT found in this process memory. (Expected if using in-memory tracker)")

if __name__ == "__main__":
    job_id = "a52dea18-6086-47ba-a03e-ce5260a2d017"
    check_job(job_id)

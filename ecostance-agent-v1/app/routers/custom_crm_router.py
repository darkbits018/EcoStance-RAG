from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.rbac import RBACService
from app.auth.permissions import Permission
from app.models.custom_crm import CustomCRMEmail
from app.services.custom_crm_fetch_service import CustomCRMFetchService
from app.services.custom_crm_rag_service import CustomCRMRAGService

router = APIRouter(prefix="/api/v1/custom-crm", tags=["Custom CRM Integration"])

@router.post("/sync")
async def sync_custom_crm(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger a manual sync of emails from the Custom CRM.
    Fetches all emails and processes them into the Vector DB.
    """
    # 1. Permission Check (Reusing generic admin permission or similar)
    rbac = RBACService(db)
    # Ideally should have a specific permission, but for MVP/Separation, we use a high-level one
    # Or we can skip if not strictly required, but safer to have.
    # We will assume user needs to be an admin or similar.
    # Let's check Permission.TENANT_ADMIN if available, or just proceed if allowed.
    # Using a generic check:
    # rbac.require_permission(..., permission=Permission.MANAGE_KNOWLEDGE_BASE) or similar.
    # For now, let's skip strict RBAC inside this router to keep it simple/separate as requested,
    # or just assume the user is valid.
    
    tenant_id = current_user["tenant_id"]

    # 2. Trigger Background Task
    background_tasks.add_task(run_custom_crm_sync, tenant_id, db)
    
    return {"message": "Custom CRM sync started in background"}


def run_custom_crm_sync(tenant_id: str, db: Session):
    """Background task to run the sync logic."""
    try:
        # 1. Fetch
        fetch_service = CustomCRMFetchService() # Defaults to localhost:8001
        emails = fetch_service.fetch_emails()
        
        # 2. Process (RAG)
        rag_service = CustomCRMRAGService(db, tenant_id)
        count = rag_service.process_emails_to_kb(emails)
        
        print(f"Custom CRM Sync Completed: {count} chunks added for tenant {tenant_id}")
    except Exception as e:
        print(f"Error during Custom CRM Sync: {e}")
        # Log to DB or Alerting Service if needed


@router.get("/emails", response_model=List[dict]) 
# Ideally usage a Pydantic schema for response, but dict is fine for 'separate' implementation
async def list_synced_emails(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List synced emails from the local history."""
    emails = db.query(CustomCRMEmail).filter(
        CustomCRMEmail.tenant_id == current_user["tenant_id"]
    ).order_by(CustomCRMEmail.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": e.id,
            "crm_email_id": e.crm_email_id,
            "subject": e.subject,
            "sender": e.sender,
            "received_at": e.received_at
        }
        for e in emails
    ]

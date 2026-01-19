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
    # 1. Permission Check

    # 1. Permission Check
    # rbac = RBACService(db)
    # rbac.require_permission(
    #     tenant_id=current_user["tenant_id"],
    #     user_id=current_user["user_id"],
    #     permission=Permission.CUSTOM_CRM_SYNC
    # )
    
    tenant_id = current_user["tenant_id"]

    # 2. Trigger Background Task
    background_tasks.add_task(run_custom_crm_sync, tenant_id, db)
    
    return {"message": "Custom CRM sync started in background"}


def run_custom_crm_sync(tenant_id: str, db: Session):
    """Background task to run the sync logic."""
    try:
        # Create a new session for the background thread if db session is closed (FastAPI depends closes it)
        # But here 'db' is passed from the request. 
        # Ideally we should create a new session.
        # But for 'BackgroundTasks' fastAPI documentation says: 
        # "If you use a dependency in a background task, you need to be careful..."
        # It's safer to use a new session.
        
        from app.db.database import SessionLocal
        session = SessionLocal()
        try:
            # 1. Fetch
            fetch_service = CustomCRMFetchService() # Defaults to localhost:8001
            emails = fetch_service.fetch_emails()
            
            # 2. Process (RAG)
            rag_service = CustomCRMRAGService(session, tenant_id)
            count = rag_service.process_emails_to_kb(emails)
            
            print(f"Custom CRM Sync Completed: {count} chunks added for tenant {tenant_id}")
        finally:
            session.close()
            
    except Exception as e:
        print(f"Error during Custom CRM Sync: {e}")


@router.get("/emails", response_model=List[dict]) 
async def list_synced_emails(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List synced emails from the local history."""
    rbac = RBACService(db)
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.CUSTOM_CRM_VIEW
    )

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

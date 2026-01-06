"""
Gmail API Router.
Handles OAuth configuration, recipient management, and scheduling.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.rbac import RBACService
from app.auth.permissions import Permission

from app.models.gmail import GmailRecipient, GmailSchedule, GmailExecutionLog
from app.schemas.gmail import (
    GmailRecipientCreate, GmailRecipientUpdate, GmailRecipientResponse,
    GmailScheduleCreate, GmailScheduleUpdate, GmailScheduleResponse,
    GmailAuthResponse, GmailCallbackRequest
)
from app.services.gmail_auth_service import GmailAuthService

router = APIRouter(prefix="/api/v1/gmail", tags=["Gmail Integration"])

# --- OAuth Configuration ---

@router.get("/auth", response_model=GmailAuthResponse)
async def get_gmail_auth_url(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the Google OAuth authorization URL to start the connection process.
    Requires: GMAIL_CONFIGURE permission
    """
    rbac = RBACService(db)
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.GMAIL_CONFIGURE
    )
    
    auth_service = GmailAuthService(db)
    auth_url = auth_service.get_authorization_url(current_user["tenant_id"])
    
    return {"auth_url": auth_url}


@router.post("/callback")
async def gmail_auth_callback(
    request: GmailCallbackRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Exchange the authorization code for tokens.
    Requires: GMAIL_CONFIGURE permission
    """
    rbac = RBACService(db)
    rbac.require_permission(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        permission=Permission.GMAIL_CONFIGURE
    )
    
    auth_service = GmailAuthService(db)
    try:
        result = auth_service.exchange_code_for_token(request.code, current_user["tenant_id"])
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Recipient Management ---

@router.get("/recipients", response_model=List[GmailRecipientResponse])
async def list_recipients(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all monitored Gmail recipients."""
    rbac = RBACService(db)
    rbac.require_permission(
        tenant_id=current_user["tenant_id"], 
        user_id=current_user["user_id"], 
        permission=Permission.GMAIL_MANAGE_RECIPIENTS
    )
    
    recipients = db.query(GmailRecipient).filter(
        GmailRecipient.tenant_id == current_user["tenant_id"]
    ).all()
    return recipients

@router.post("/recipients", response_model=GmailRecipientResponse)
async def create_recipient(
    recipient_data: GmailRecipientCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add a new recipient to monitor."""
    rbac = RBACService(db)
    rbac.require_permission(
        tenant_id=current_user["tenant_id"], 
        user_id=current_user["user_id"], 
        permission=Permission.GMAIL_MANAGE_RECIPIENTS
    )
    
    new_recipient = GmailRecipient(
        tenant_id=current_user["tenant_id"],
        email_address=recipient_data.email_address,
        display_name=recipient_data.display_name,
        group_name=recipient_data.group_name,
        enabled=recipient_data.enabled,
        filters=recipient_data.filters
    )
    db.add(new_recipient)
    db.commit()
    db.refresh(new_recipient)
    return new_recipient

@router.delete("/recipients/{recipient_id}")
async def delete_recipient(
    recipient_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Remove a monitored recipient."""
    rbac = RBACService(db)
    rbac.require_permission(
        tenant_id=current_user["tenant_id"], 
        user_id=current_user["user_id"], 
        permission=Permission.GMAIL_MANAGE_RECIPIENTS
    )
    
    recipient = db.query(GmailRecipient).filter(
        GmailRecipient.id == recipient_id,
        GmailRecipient.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
        
    db.delete(recipient)
    db.commit()
    return {"message": "Recipient deleted"}

# --- Schedule Management ---

@router.get("/schedules", response_model=List[GmailScheduleResponse])
async def list_schedules(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all Gmail sync schedules."""
    rbac = RBACService(db)
    rbac.require_permission(
        tenant_id=current_user["tenant_id"], 
        user_id=current_user["user_id"], 
        permission=Permission.GMAIL_MANAGE_SCHEDULES
    )
    
    schedules = db.query(GmailSchedule).filter(
        GmailSchedule.tenant_id == current_user["tenant_id"]
    ).all()
    return schedules

@router.post("/schedules", response_model=GmailScheduleResponse)
async def create_schedule(
    schedule_data: GmailScheduleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new sync schedule."""
    rbac = RBACService(db)
    rbac.require_permission(
        tenant_id=current_user["tenant_id"], 
        user_id=current_user["user_id"], 
        permission=Permission.GMAIL_MANAGE_SCHEDULES
    )
    
    new_schedule = GmailSchedule(
        tenant_id=current_user["tenant_id"],
        name=schedule_data.name,
        schedule_type=schedule_data.schedule_type,
        schedule_config=schedule_data.schedule_config,
        recipient_ids=schedule_data.recipient_ids,
        enabled=schedule_data.enabled
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule


@router.post("/schedules/{schedule_id}/sync")
async def sync_schedule_now(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger a Gmail sync schedule."""
    # 1. Permission Check
    rbac = RBACService(db)
    rbac.require_permission(
        tenant_id=current_user["tenant_id"], 
        user_id=current_user["user_id"], 
        permission=Permission.GMAIL_EXECUTE_SYNC
    )
    
    # 2. Get Schedule
    schedule = db.query(GmailSchedule).filter(
        GmailSchedule.id == schedule_id,
        GmailSchedule.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # 3. Trigger Sync via Scheduler Service
    from app.services.scheduler_service import get_scheduler
    scheduler = get_scheduler()
    
    # We run this in a separate thread so the API returns quickly? 
    # Or synchronously to show result? 
    # For "Sync Now" usually users want confirmation it started. 
    # Since _execute_gmail_schedule is blocking, ideally we background it.
    # But for MVP, running it inline is fine if it's not too long, 
    # or better: we use the scheduler's logic but don't block.
    # Actually, let's run it synchronously so we can return success/failure immediately for testing.
    # The user asked for "Sync Now", implying immediate action.
    
    try:
        scheduler.execute_schedule_now(db, schedule)
        return {"message": "Sync completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


# --- Message History ---

from app.models.gmail import GmailMessage
from app.schemas.gmail import GmailMessageResponse

@router.get("/messages", response_model=List[GmailMessageResponse])
async def list_messages(
    limit: int = Query(50, ge=1, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List history of ingested Gmail messages."""
    rbac = RBACService(db)
    # Reusing VIEW permission for now, or could define a new GMAIL_VIEW_MESSAGES
    rbac.require_permission(
        tenant_id=current_user["tenant_id"], 
        user_id=current_user["user_id"], 
        permission=Permission.GMAIL_MANAGE_RECIPIENTS # Use existing permission for MVP
    )
    
    messages = db.query(GmailMessage).filter(
        GmailMessage.tenant_id == current_user["tenant_id"]
    ).order_by(GmailMessage.received_at.desc()).offset(offset).limit(limit).all()
    
    return messages


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an ingested Gmail message.
    Removes the record from SQL history AND deletes associated vectors from Qdrant.
    """
    rbac = RBACService(db)
    rbac.require_permission(
        tenant_id=current_user["tenant_id"], 
        user_id=current_user["user_id"], 
        permission=Permission.GMAIL_MANAGE_RECIPIENTS # Reuse existing permission
    )
    
    # 1. Find the message
    message = db.query(GmailMessage).filter(
        GmailMessage.id == message_id,
        GmailMessage.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # 2. Delete from Qdrant
    # We need the physical collection name.
    # We can perform a query to find the KB first.
    from app.services.tenant_service import get_tenant_service
    from app.services.qdrant_service import get_qdrant_client, delete_points_by_metadata
    
    qdrant_client = get_qdrant_client()
    tenant_service = get_tenant_service(qdrant_client)
    collection_name = tenant_service.get_collection_name(current_user["tenant_id"], "gmail_emails")
    
    # The payload stores 'email_id' as the original Gmail ID (message.gmail_message_id)
    try:
        delete_points_by_metadata(qdrant_client, collection_name, "email_id", message.gmail_message_id)
    except Exception as e:
        # Log error but proceed to delete record? Or fail?
        # Proceeding is safer to ensure eventual consistency if Qdrant is down but we want to clean UI.
        # But failing is better for data integrity. Let's fail for now.
        raise HTTPException(status_code=500, detail=f"Failed to delete from vector store: {e}")

    # 3. Delete from SQL
    db.delete(message)
    db.commit()
    
    return {"message": "Message and vectors deleted successfully"}

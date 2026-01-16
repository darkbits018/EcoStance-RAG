"""
Gmail API Schemas.
Request and response models for Gmail integration.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Recipients ---

class GmailRecipientBase(BaseModel):
    email_address: EmailStr
    display_name: Optional[str] = None
    group_name: Optional[str] = None
    enabled: bool = True
    filters: Optional[Dict[str, Any]] = None

class GmailRecipientCreate(GmailRecipientBase):
    pass

class GmailRecipientUpdate(BaseModel):
    display_name: Optional[str] = None
    group_name: Optional[str] = None
    enabled: Optional[bool] = None
    filters: Optional[Dict[str, Any]] = None

class GmailRecipientResponse(GmailRecipientBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Schedules ---

class GmailScheduleBase(BaseModel):
    name: str
    schedule_type: str  # 'interval', 'daily', 'weekly'
    schedule_config: Dict[str, Any]
    recipient_ids: List[str] = []
    enabled: bool = True

class GmailScheduleCreate(GmailScheduleBase):
    pass

class GmailScheduleUpdate(BaseModel):
    name: Optional[str] = None
    schedule_type: Optional[str] = None
    schedule_config: Optional[Dict[str, Any]] = None
    recipient_ids: Optional[List[str]] = None
    enabled: Optional[bool] = None

class GmailScheduleResponse(GmailScheduleBase):
    id: str
    tenant_id: str
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- OAuth ---

class GmailAuthResponse(BaseModel):
    auth_url: str

class GmailCallbackRequest(BaseModel):
    code: str


# --- Messages ---

class GmailMessageResponse(BaseModel):
    id: str
    tenant_id: str
    gmail_message_id: str
    thread_id: Optional[str] = None
    subject: Optional[str] = None
    sender: Optional[str] = None
    snippet: Optional[str] = None
    received_at: Optional[datetime] = None
    ingested_at: datetime

    class Config:
        from_attributes = True

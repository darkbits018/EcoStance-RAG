from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
import uuid

class CustomCRMEmail(SQLModel, table=True):
    """
    Tracks emails ingested from the Custom CRM to prevent invalid duplicates.
    This table maps the CRM's email ID to the Tenant's workspace.
    """
    __tablename__ = "custom_crm_emails"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: str = Field(index=True, nullable=False)
    
    # The ID from the Custom CRM (Gmail Message ID or internal UUID)
    crm_email_id: str = Field(index=True, nullable=False)
    
    # Metadata for display/history
    subject: Optional[str] = None
    sender: Optional[str] = None
    received_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

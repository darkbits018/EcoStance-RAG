from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

# Forward reference for EmailDumpTask if needed, but for now simple link via ID
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.dump import EmailDumpTask

class Email(SQLModel, table=True):
    id: str = Field(primary_key=True) # Gmail Message ID
    thread_id: str = Field(index=True)
    dump_task_id: uuid.UUID = Field(index=True, default=None, nullable=True)
    sender: str
    recipients: str # Comma separated
    subject: Optional[str] = None
    snippet: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    received_at: datetime
    labels: str # JSON string of labels
    
    # We might want to link emails to dumps, but usually an email exists once. 
    # A dump is just a collection of criterias.
    # If we want to know WHICH dump brought this email, we can use a link table 
    # or just keep it loose. For simplicity, let's keep emails unique by ID.

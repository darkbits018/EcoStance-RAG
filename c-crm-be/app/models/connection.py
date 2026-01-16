from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class GmailConnection(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email_address: str = Field(index=True, unique=True)
    access_token: str
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

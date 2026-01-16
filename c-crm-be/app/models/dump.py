from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid

class DumpStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class CriteriaType(str, Enum):
    LABEL = "LABEL"
    RECIPIENT = "RECIPIENT"

class EmailDumpTask(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    connection_id: uuid.UUID
    status: DumpStatus = Field(default=DumpStatus.PENDING)
    criteria_type: CriteriaType
    criteria_value: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_emails: int = Field(default=0)
    error_message: Optional[str] = None

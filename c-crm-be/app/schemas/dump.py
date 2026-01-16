from pydantic import BaseModel
from typing import Optional
from enum import Enum
import uuid
from datetime import datetime

class CriteriaType(str, Enum):
    LABEL = "LABEL"
    RECIPIENT = "RECIPIENT"

class DumpCreate(BaseModel):
    connection_id: uuid.UUID
    criteria_type: CriteriaType
    criteria_value: str

class DumpRead(BaseModel):
    id: uuid.UUID
    status: str
    total_emails: int
    started_at: datetime
    completed_at: Optional[datetime]
    criteria_type: str
    criteria_value: str

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EmailRead(BaseModel):
    id: str
    thread_id: str
    sender: str
    recipients: Optional[str] = ""
    subject: Optional[str] = ""
    snippet: Optional[str] = ""
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    received_at: datetime
    labels: str

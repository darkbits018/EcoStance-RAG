"""
Gmail Integration Models.
Defines tables for storing recipients, schedules, and execution logs.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..db.database import Base

class GmailRecipient(Base):
    __tablename__ = "gmail_recipients"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), nullable=True, index=True) # The user who owns this recipient
    
    email_address = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    group_name = Column(String(100), nullable=True)
    
    enabled = Column(Boolean, default=True)
    filters = Column(JSON, default=dict)  # Search filters like subject keywords, exclusions
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", backref="gmail_recipients")


class GmailSchedule(Base):
    __tablename__ = "gmail_schedules"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), nullable=True, index=True) # The user who created this schedule
    
    name = Column(String(255), nullable=False)
    schedule_type = Column(String(50), nullable=False)  # 'interval', 'daily', 'weekly'
    schedule_config = Column(JSON, nullable=False)  # e.g., {"minutes": 60} or {"time": "14:00"}
    
    recipient_ids = Column(JSON, default=list)  # List of recipient IDs to sync
    
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", backref="gmail_schedules")


class GmailExecutionLog(Base):
    __tablename__ = "gmail_execution_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), nullable=True, index=True)
    
    schedule_id = Column(String(36), ForeignKey("gmail_schedules.id", ondelete="SET NULL"), nullable=True)
    recipient_id = Column(String(36), ForeignKey("gmail_recipients.id", ondelete="SET NULL"), nullable=True)
    
    execution_type = Column(String(50), nullable=False)  # 'scheduled', 'manual'
    status = Column(String(50), nullable=False)  # 'success', 'failed', 'partial'
    
    emails_processed = Column(Integer, default=0)
    emails_added = Column(Integer, default=0)
    errors = Column(JSON, nullable=True)
    
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)


class GmailMessage(Base):
    __tablename__ = "gmail_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), nullable=True, index=True) # The user who owns/ingested this message
    
    gmail_message_id = Column(String(255), nullable=False) # The actual ID from Gmail
    thread_id = Column(String(255), nullable=True)
    
    subject = Column(String(500), nullable=True)
    sender = Column(String(255), nullable=True)
    snippet = Column(String(1000), nullable=True)
    
    received_at = Column(DateTime, nullable=True) # Date from email header
    ingested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", backref="gmail_messages")

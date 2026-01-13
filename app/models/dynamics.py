"""
Dynamics 365 Models.
Defines tables for storing Dynamics email history.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..db.database import Base

class DynamicsMessage(Base):
    __tablename__ = "dynamics_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    activity_id = Column(String(255), nullable=False, index=True) # Dynamics GUID
    
    subject = Column(String(500), nullable=True)
    sender = Column(String(255), nullable=True)
    raw_body = Column(Text, nullable=True) # Dynamics bodies can be large
    
    created_at = Column(DateTime, nullable=True) # CreatedOn in Dynamics
    ingested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", backref="dynamics_messages")

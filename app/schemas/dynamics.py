"""
Dynamics 365 Schemas.
Request and response models for Dynamics 365 CRM integration.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class DynamicsConfigCreate(BaseModel):
    """Configuration for connecting to Dynamics 365."""
    tenant_id: str
    client_id: str
    client_secret: str
    resource_url: str  # e.g., https://org12345.crm.dynamics.com

class DynamicsConfigResponse(BaseModel):
    """Response model for Dynamics configuration (hides secret)."""
    tenant_id: str
    client_id: str
    resource_url: str
    is_configured: bool
    last_sync: Optional[datetime] = None

class DynamicsTestResponse(BaseModel):
    """Result of a connection test."""
    success: bool
    message: str
    user_email: Optional[str] = None

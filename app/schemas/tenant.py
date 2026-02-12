"""
Tenant schemas for request/response models.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class TenantProfileUpdate(BaseModel):
    """Schema for updating tenant profile."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class NotificationPreferences(BaseModel):
    """Schema for notification preferences."""
    email_alerts: bool = True
    quota_warnings: bool = True
    error_alerts: bool = True
    weekly_reports: bool = False
    webhook_url: Optional[str] = None


class TenantCreateRequest(BaseModel):
    """Tenant creation request model."""
    name: str
    email: str
    password: str
    phone: Optional[str] = None
    billing_tier: str = "free_trial"


class TenantUpdateRequest(BaseModel):
    """Tenant update request model."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    billing_tier: Optional[str] = None
    settings: Optional[dict] = None


class TenantResponse(BaseModel):
    """Tenant response model."""
    id: str
    name: str
    slug: str
    email: Optional[str]
    phone: Optional[str]
    is_active: bool
    created_at: datetime
    billing_tier: Optional[str] = "free_trial"
    billing_status: Optional[str] = "active"
    logo_url: Optional[str] = None
    logo_filename: Optional[str] = None
    trial_ends_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TenantWithPreferences(TenantResponse):
    """Tenant response with preferences."""
    preferences: Optional[NotificationPreferences] = None

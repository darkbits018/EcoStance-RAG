from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class TenantUserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

class TenantUserCreate(TenantUserBase):
    role_id: Optional[str] = None
    password: str  # Required for new user creation
    # Password field would be here if we were handling auth locally for users
    # For now, we assume invitation flow or external auth

class TenantUserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[str] = None

class TenantUserResponse(TenantUserBase):
    id: str
    tenant_id: str
    user_id: str
    system_role: Optional[str] = None
    tenant_role_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    
    # Include role details if available
    role_name: Optional[str] = None

    class Config:
        from_attributes = True

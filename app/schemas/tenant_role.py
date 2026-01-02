"""
Pydantic schemas for TenantRole operations.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.auth.permissions import Permission


class TenantRoleBase(BaseModel):
    """Base schema for TenantRole."""
    name: str = Field(..., min_length=1, max_length=100, description="Role name")
    description: Optional[str] = Field(None, max_length=500, description="Role description")
    permissions: List[Permission] = Field(default_factory=list, description="List of permissions")
    is_active: bool = Field(True, description="Whether the role is active")


class TenantRoleCreate(TenantRoleBase):
    """Schema for creating a new tenant role."""
    pass


class TenantRoleUpdate(BaseModel):
    """Schema for updating a tenant role."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Role name")
    description: Optional[str] = Field(None, max_length=500, description="Role description")
    permissions: Optional[List[Permission]] = Field(None, description="List of permissions")
    is_active: Optional[bool] = Field(None, description="Whether the role is active")


class TenantRoleResponse(TenantRoleBase):
    """Schema for tenant role responses."""
    id: str
    tenant_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TenantRoleListResponse(BaseModel):
    """Schema for listing tenant roles."""
    roles: List[TenantRoleResponse]
    total: int


class AssignRoleRequest(BaseModel):
    """Schema for assigning a role to a user."""
    user_id: str = Field(..., description="User ID to assign role to")
    role_id: str = Field(..., description="Role ID to assign")


class RemoveRoleRequest(BaseModel):
    """Schema for removing a role from a user."""
    user_id: str = Field(..., description="User ID to remove role from")
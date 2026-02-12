"""
TenantRole model - represents custom roles within a tenant.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..db.database import Base


class TenantRole(Base):
    __tablename__ = "tenant_roles"
    __table_args__ = (
        UniqueConstraint('tenant_id', 'name', name='unique_tenant_role_name'),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # e.g., "HR Manager", "Sales Rep"
    description = Column(String(500))
    permissions = Column(JSON, default=list)  # List of permission strings
    is_active = Column(Boolean, default=True)
    created_by = Column(String(36), ForeignKey("tenant_users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="roles")
    creator = relationship("TenantUser", foreign_keys=[created_by], post_update=True)
    users = relationship("TenantUser", foreign_keys="TenantUser.tenant_role_id", back_populates="tenant_role")
    
    def __repr__(self):
        return f"<TenantRole(id={self.id}, tenant_id={self.tenant_id}, name={self.name})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "description": self.description,
            "permissions": self.permissions,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
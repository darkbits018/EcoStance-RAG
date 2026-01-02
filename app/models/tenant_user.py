"""
TenantUser model - represents users and their roles within a tenant.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..db.database import Base


class TenantUser(Base):
    __tablename__ = "tenant_users"
    __table_args__ = (
        UniqueConstraint('tenant_id', 'user_id', name='unique_tenant_user'),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)  # Reference to user in auth system
    
    # User information
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=True)  # Hashed password for authentication
    full_name = Column(String(255))
    
    # Enhanced role system
    system_role = Column(String(50), nullable=True)  # "super_admin" or "tenant_admin"
    tenant_role_id = Column(String(36), ForeignKey("tenant_roles.id"), nullable=True)
    
    # Legacy role field (kept for backward compatibility during migration)
    role = Column(String(50), nullable=True, default="user")  # Will be deprecated
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    tenant_role = relationship("TenantRole", foreign_keys=[tenant_role_id], back_populates="users")
    
    def __repr__(self):
        return f"<TenantUser(id={self.id}, tenant_id={self.tenant_id}, user_id={self.user_id}, role={self.role})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "email": self.email,
            "full_name": self.full_name,
            "system_role": self.system_role,
            "tenant_role_id": self.tenant_role_id,
            "role": self.role,  # Legacy field
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None
        }

"""
Billing models for tracking subscriptions and transactions.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship

from ..db.database import Base


class BillingSubscription(Base):
    """
    Tracks the active subscription and billing lifecycle for a tenant.
    """
    __tablename__ = "billing_subscriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    provider = Column(String(50), nullable=False)  # 'stripe', 'razorpay'
    provider_subscription_id = Column(String(255), unique=True, index=True)
    provider_customer_id = Column(String(255), index=True)
    
    plan_id = Column(String(50), nullable=False)  # 'business', 'enterprise'
    status = Column(String(50), nullable=False, default="active")  # 'active', 'past_due', 'canceled', 'trialing'
    
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    tenant = relationship("Tenant", back_populates="subscription")


class BillingTransaction(Base):
    """
    Records individual payment transactions from Stripe or Razorpay.
    """
    __tablename__ = "billing_transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    provider = Column(String(50), nullable=False)  # 'stripe', 'razorpay'
    provider_transaction_id = Column(String(255), unique=True, index=True)
    provider_order_id = Column(String(255), index=True)  # Razorpay order_id or Stripe session_id
    
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(String(50), nullable=False)  # 'succeeded', 'failed', 'pending'
    
    payment_method = Column(String(50))  # 'card', 'upi', etc.
    billing_email = Column(String(255))
    
    # Metadata for custom properties (BYOK addons, extra storage purchased)
    metadata_json = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    tenant = relationship("Tenant", back_populates="transactions")

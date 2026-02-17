import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from .stripe_provider import StripeProvider
from .razorpay_provider import RazorpayProvider
from ...models.tenant import Tenant
from ...models.billing import BillingSubscription, BillingTransaction
from ...services.quota_service import QuotaService

logger = logging.getLogger(__name__)

class BillingService:
    def __init__(self, db: Session):
        self.db = db
        self.providers = {
            "stripe": StripeProvider(),
            "razorpay": RazorpayProvider()
        }
        self.quota_service = QuotaService(db)

    async def create_checkout(self, tenant_id: str, plan_id: str, currency: str = "USD") -> Dict[str, Any]:
        """
        Entry point to create a checkout session.
        Routes to Stripe for USD and Razorpay for INR.
        """
        # Determine provider based on currency
        provider_name = "razorpay" if currency.upper() == "INR" else "stripe"
        provider = self.providers.get(provider_name)
        
        # Define amounts (Example logic - move to a config/DB later)
        plan_prices = {
            "business": {"USD": 29.0, "INR": 2499.0},
            "enterprise": {"USD": 199.0, "INR": 14999.0}
        }
        
        price_info = plan_prices.get(plan_id, plan_prices["business"])
        amount = price_info.get(currency.upper(), price_info["USD"])
        
        # Base URLs (Move to config/env)
        base_url = "http://localhost:3000" # Frontend URL
        
        return await provider.create_checkout_session(
            tenant_id=tenant_id,
            plan_id=plan_id,
            amount=amount,
            currency=currency,
            success_url=f"{base_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/billing/cancel"
        )

    async def fulfill_order(self, tenant_id: str, plan_id: str, provider: str, provider_subs_id: str, provider_cust_id: str = None):
        """
        The "Master Fulfillment" logic. Updates DB and Quotas.
        """
        try:
            tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant:
                logger.error(f"Tenant {tenant_id} not found during fulfillment")
                return False

            # 1. Update Tenant Tier
            tenant.billing_tier = plan_id
            tenant.billing_status = "active"
            tenant.trial_ends_at = None # Clear trial status
            
            # 2. Update Subscription Record
            subscription = self.db.query(BillingSubscription).filter(BillingSubscription.tenant_id == tenant_id).first()
            if not subscription:
                subscription = BillingSubscription(tenant_id=tenant_id)
                self.db.add(subscription)
            
            subscription.provider = provider
            subscription.provider_subscription_id = provider_subs_id
            subscription.provider_customer_id = provider_cust_id
            subscription.plan_id = plan_id
            subscription.status = "active"
            subscription.updated_at = datetime.utcnow()

            # 3. Update Quotas
            new_quotas = QuotaService.TIER_QUOTAS.get(plan_id)
            if new_quotas:
                self.quota_service.update_tenant_quotas(tenant_id, new_quotas)
                # Sync to tenant settings for legacy display
                settings = tenant.settings or {}
                settings.update(new_quotas)
                tenant.settings = settings

            self.db.commit()
            logger.info(f"✓ Successfully fulfilled {plan_id} upgrade for tenant {tenant_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Fulfillment failed for tenant {tenant_id}: {str(e)}")
            return False

    def record_transaction(self, tenant_id: str, provider: str, tx_id: str, order_id: str, amount: float, currency: str, status: str):
        """
        Audit trail for payments.
        """
        transaction = BillingTransaction(
            tenant_id=tenant_id,
            provider=provider,
            provider_transaction_id=tx_id,
            provider_order_id=order_id,
            amount=amount,
            currency=currency,
            status=status
        )
        self.db.add(transaction)
        self.db.commit()

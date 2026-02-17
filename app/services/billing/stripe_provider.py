import stripe
import os
from typing import Dict, Any, Optional
from .interface import PaymentProvider

class StripeProvider(PaymentProvider):
    def __init__(self):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    async def create_checkout_session(self, tenant_id: str, plan_id: str, amount: float, currency: str, success_url: str, cancel_url: str) -> Dict[str, Any]:
        """
        Creates a Stripe Checkout Session.
        """
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency.lower(),
                    'product_data': {
                        'name': f"EcoStance Agent - {plan_id.capitalize()} Plan",
                    },
                    'unit_amount': int(amount * 100), # Stripe expects cents
                    'recurring': {'interval': 'month'},
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'tenant_id': tenant_id,
                'plan_id': plan_id
            }
        )
        return {
            "provider": "stripe",
            "checkout_url": session.url,
            "session_id": session.id
        }

    async def verify_webhook(self, payload: Any, signature: str) -> Dict[str, Any]:
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return {
                "verified": True,
                "event_type": event['type'],
                "data": event['data']['object'],
                "raw_event": event
            }
        except Exception as e:
            return {"verified": False, "error": str(e)}

    async def get_subscription_details(self, subscription_id: str) -> Dict[str, Any]:
        subs = stripe.Subscription.retrieve(subscription_id)
        return {
            "status": subs.status,
            "current_period_end": subs.current_period_end,
            "cancel_at_period_end": subs.cancel_at_period_end
        }

    async def cancel_subscription(self, subscription_id: str) -> bool:
        try:
            stripe.Subscription.delete(subscription_id)
            return True
        except:
            return False

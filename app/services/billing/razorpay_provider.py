import razorpay
import os
import hmac
import hashlib
from typing import Dict, Any, Optional
from .interface import PaymentProvider

class RazorpayProvider(PaymentProvider):
    def __init__(self):
        self.client = razorpay.Client(
            auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
        )
        self.webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")

    async def create_checkout_session(self, tenant_id: str, plan_id: str, amount: float, currency: str, success_url: str, cancel_url: str) -> Dict[str, Any]:
        """
        Creates a Razorpay Order.
        """
        data = {
            "amount": int(amount * 100), # Razorpay expects paise
            "currency": currency.upper(),
            "receipt": f"receipt_{tenant_id[:8]}",
            "notes": {
                "tenant_id": tenant_id,
                "plan_id": plan_id
            }
        }
        order = self.client.order.create(data=data)
        
        return {
            "provider": "razorpay",
            "order_id": order['id'],
            "amount": order['amount'],
            "currency": order['currency'],
            "key_id": os.getenv("RAZORPAY_KEY_ID")
        }

    async def verify_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """
        Verify Razorpay webhook signature.
        """
        try:
            # Razorpay expects binary payload for verification
            self.client.utility.verify_webhook_signature(
                payload.decode('utf-8'), 
                signature, 
                self.webhook_secret
            )
            import json
            data = json.loads(payload)
            return {
                "verified": True,
                "event_type": data['event'],
                "data": data['payload']['payment']['entity'] if 'payment' in data['payload'] else data['payload'],
                "raw_event": data
            }
        except Exception as e:
            return {"verified": False, "error": str(e)}

    async def get_subscription_details(self, subscription_id: str) -> Dict[str, Any]:
        # Razorpay subscription retrieval
        subs = self.client.subscription.fetch(subscription_id)
        return {
            "status": subs['status'],
            "current_period_end": subs['current_end'],
            "cancel_at_period_end": subs['pause_at_period_end'] if 'pause_at_period_end' in subs else False
        }

    async def cancel_subscription(self, subscription_id: str) -> bool:
        try:
            self.client.subscription.cancel(subscription_id)
            return True
        except:
            return False

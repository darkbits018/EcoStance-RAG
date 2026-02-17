from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class PaymentProvider(ABC):
    """
    Abstract base class for payment providers.
    """
    
    @abstractmethod
    async def create_checkout_session(self, tenant_id: str, plan_id: str, amount: float, currency: str, success_url: str, cancel_url: str) -> Dict[str, Any]:
        """
        Create a checkout session/order and return details (URL or OrderID).
        """
        pass

    @abstractmethod
    async def verify_webhook(self, payload: Any, signature: str) -> Dict[str, Any]:
        """
        Verify the webhook signature and parse the event data.
        """
        pass

    @abstractmethod
    async def get_subscription_details(self, subscription_id: str) -> Dict[str, Any]:
        """
        Fetch current status and period details for a subscription.
        """
        pass

    @abstractmethod
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """
        Cancel an active subscription.
        """
        pass

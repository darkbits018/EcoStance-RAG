from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..db.database import get_db
from ..services.billing.billing_service import BillingService
from ..auth.dependencies import get_tenant_id

router = APIRouter(prefix="/billing", tags=["Billing & Payments"])

from pydantic import BaseModel

class CheckoutRequest(BaseModel):
    plan_id: str
    currency: str = "USD"

@router.post("/checkout")
async def create_checkout(
    request_data: CheckoutRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    plan_id = request_data.plan_id
    currency = request_data.currency
    """
    Create a checkout session for a specific plan.
    Supported plans: business, enterprise
    """
    if plan_id not in ["business", "enterprise"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan selected"
        )
    
    billing_service = BillingService(db)
    try:
        checkout_info = await billing_service.create_checkout(tenant_id, plan_id, currency)
        return checkout_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhook events.
    """
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    
    billing_service = BillingService(db)
    stripe_provider = billing_service.providers["stripe"]
    
    result = await stripe_provider.verify_webhook(payload, sig_header)
    if not result["verified"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    event_type = result["event_type"]
    data = result["data"]
    
    if event_type == "checkout.session.completed":
        tenant_id = data.get("metadata", {}).get("tenant_id")
        plan_id = data.get("metadata", {}).get("plan_id")
        subs_id = data.get("subscription")
        cust_id = data.get("customer")
        
        if tenant_id and plan_id:
            await billing_service.fulfill_order(tenant_id, plan_id, "stripe", subs_id, cust_id)
            billing_service.record_transaction(
                tenant_id=tenant_id,
                provider="stripe",
                tx_id=data.get("payment_intent") or subs_id,
                order_id=data.get("id"),
                amount=data.get("amount_total") / 100,
                currency=data.get("currency").upper(),
                status="succeeded"
            )

    return {"status": "success"}

@router.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Razorpay webhook events.
    """
    payload = await request.body()
    sig_header = request.headers.get("X-Razorpay-Signature")
    
    billing_service = BillingService(db)
    razorpay_provider = billing_service.providers["razorpay"]
    
    result = await razorpay_provider.verify_webhook(payload, sig_header)
    if not result["verified"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    event_type = result["event_type"]
    data = result["data"]
    
    if event_type == "payment.captured":
        # Extract metadata from notes
        notes = data.get("notes", {})
        tenant_id = notes.get("tenant_id")
        plan_id = notes.get("plan_id")
        
        if tenant_id and plan_id:
            await billing_service.fulfill_order(tenant_id, plan_id, "razorpay", data.get("id"))
            billing_service.record_transaction(
                tenant_id=tenant_id,
                provider="razorpay",
                tx_id=data.get("id"),
                order_id=data.get("order_id"),
                amount=data.get("amount") / 100,
                currency=data.get("currency").upper(),
                status="succeeded"
            )

    return {"status": "success"}

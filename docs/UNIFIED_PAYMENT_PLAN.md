# Unified Payment System (UPS) - Implementation Plan

## 1. Objective
Build a vendor-agnostic billing architecture that supports multiple payment providers (**Stripe** for global card payments and **Razorpay** for Indian UPI/Local payments) while maintaining a single, unified source of truth for Tenant Tiers and Quotas.

---

## 2. Core Architecture: The "Billing Bridge"

We will use an **Interface-based approach** to prevent vendor lock-in.

*   **`BillingProvider` (Interface)**: Defines abstract methods like `create_checkout_session()`, `cancel_subscription()`, and `handle_webhook()`.
*   **`StripeProvider` (Implementation)**: Specific logic for Stripe API.
*   **`RazorpayProvider` (Implementation)**: Specific logic for Razorpay API.
*   **`BillingService` (Orchestrator)**: The main entry point used by routers. It decides which provider to call based on user currency or location.

---

## 3. Database Schema (New Tables)

### `billing_subscriptions`
Tracks the lifecycle of a tenant's paid status.
*   `id`: UUID (Primary Key)
*   `tenant_id`: FK (tenants.id)
*   `provider`: String ('stripe', 'razorpay')
*   `provider_subscription_id`: String (The ID from Stripe/RP)
*   `status`: String (active, past_due, trialing, canceled)
*   `plan_id`: String (Identifier for Business/Enterprise)
*   `current_period_start`: DateTime
*   `current_period_end`: DateTime
*   `cancel_at_period_end`: Boolean

### `billing_invoices` / `billing_transactions`
Tracks individual payments for audit and debugging.
*   `id`: UUID
*   `tenant_id`: FK
*   `provider_transaction_id`: String
*   `amount`: Decimal
*   `currency`: String (USD, INR)
*   `status`: String (succeeded, failed, pending)

---

## 4. Implementation Phases

### Phase 1: Database Setup
- Create `subscriptions` and `transactions` tables via SQLAlchemy.
- Link them to the existing `Tenant` model via relationships.

### Phase 2: Provider Integration
- **Stripe**: Implement Stripe Checkout (Price IDs, Webhook Signatures).
- **Razorpay**: Implement Razorpay Orders API (Key/Secret, Signature verification).

### Phase 3: The Unified Fulfillment Engine (CRITICAL)
This is a single internal service function that is called by **both** Stripe and Razorpay webhooks.
```python
def fulfill_payment(tenant_id, plan_id, status):
    # 1. Update billing_subscriptions table
    # 2. Update tenants.billing_tier
    # 3. Call QuotaService.update_tenant_quotas(tenant_id, new_tier)
    # 4. Clear cache to refresh the agent's query limits immediately
```

### Phase 4: Webhook Architecture
- `POST /api/v1/billing/webhooks/stripe`: Validates Stripe-Signature.
- `POST /api/v1/billing/webhooks/razorpay`: Validates X-Razorpay-Signature.
- Both call `fulfill_payment` upon success.

---

## 5. User Workflow (Frontend)

1.  **Selection**: User selects "Business Plan" (\$29/mo).
2.  **Checkout Request**: Frontend calls `POST /api/v1/billing/checkout`.
    - Payload: `{ "plan": "business", "currency": "USD" }`.
3.  **Redirect**: 
    - If USD: Backend returns a **Stripe Checkout URL**. Frontend redirects.
    - If INR: Backend returns a **Razorpay Order ID**. Frontend opens the **Razorpay Modal**.
4.  **Completion**: User pays. Stripe/Razorpay sends a Webhook.
5.  **Activation**: Backend fulfills order. User is redirected back to `/dashboard?payment=success`.

---

## 6. Error Handling & Edge Cases
*   **Failed Payments**: If a subscription renewal fails, the webhook must downgrade the tenant to `free_trial` (restricted) or `suspended` status.
*   **Idempotency**: Use `provider_transaction_id` as a unique constraint to ensure a single payment never triggers two fulfillment cycles.
*   **Refunds**: Handle `charge.refunded` webhooks to automatically adjust tenant quotas.

---
*Created by EcoStance Backend Architecture Team - 2026*

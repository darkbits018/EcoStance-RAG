# Payment System Integration Guide (Frontend & Backend)

## 1. Overview
The EcoStance payment system is a **Unified Payment System (UPS)** that abstracts multiple payment providers (**Stripe** and **Razorpay**). The choice of provider is driven primarily by the currency:
- **USD**: Handled via Stripe (Global Cards/Wallets).
- **INR**: Handled via Razorpay (UPI/Netbanking/Local Cards).

---

## 2. API Endpoints

### Create Checkout Session
`POST /api/v1/billing/checkout`

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `plan_id` | String | Yes | `business` or `enterprise` |
| `currency` | String | No | `USD` (default) or `INR` |

**Response (Stripe):**
```json
{
  "provider": "stripe",
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_test_..."
}
```

**Response (Razorpay):**
```json
{
  "provider": "razorpay",
  "order_id": "order_PK...",
  "amount": 249900,
  "currency": "INR",
  "key_id": "rzp_test_..."
}
```

---

## 3. Frontend Implementation Requirements

### A. The "Currency Switcher"
The frontend should detect the user's location or allow them to toggle between USD and INR.
- **Switch to USD**: The UI should show Stripe-specific features (Credit Card icons).
- **Switch to INR**: The UI should showcase Razorpay/UPI options.

### B. Handling Stripe (Redirect)
When the API returns `provider: "stripe"`:
1.  Simply redirect the browser window to the `checkout_url` provided.
    `window.location.href = response.checkout_url;`

### C. Handling Razorpay (Modal)
When the API returns `provider: "razorpay"`, the frontend must use the `razorpay-js` SDK to open the modal:

```javascript
const options = {
  key: response.key_id,
  amount: response.amount,
  currency: response.currency,
  name: "EcoStance AI",
  order_id: response.order_id,
  handler: function (response) {
    // Payment successful in modal, redirect to success page
    window.location.href = "/billing/success?gateway=razorpay";
  },
  theme: { color: "#3399cc" }
};
const rzp = new Razorpay(options);
rzp.open();
```

---

## 4. Webhook and Provisioning Flow (Backend)

The frontend **NEVER** updates the tenant's tier. This is handled securely by the backend webhooks:

1.  **Stripe**: `POST /api/v1/billing/webhooks/stripe`
    - Listens for `checkout.session.completed`.
2.  **Razorpay**: `POST /api/v1/billing/webhooks/razorpay`
    - Listens for `payment.captured`.

**Actions taken on Success:**
- `tenants.billing_tier` updated to the plan ID.
- `tenants.trial_ends_at` set to `NULL`.
- `QuotaService` resets monthly query counts and raises daily limits.
- A new row is added to the `billing_transactions` table for audit.

---

## 5. Post-Payment Redirects
The backend expects the frontend to host two static routes:
- `/billing/success`: Show a "Thank you! Your account is now upgraded" message. Recommend refreshing the page to see new limits.
- `/billing/cancel`: Show a "Payment cancelled" message and allow them to try again.

---

## 6. Environment Check (Action Required)
Ensure the following are updated in the `.env` file for the backend to function:
- `STRIPE_SECRET_KEY` & `STRIPE_WEBHOOK_SECRET`
- `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, & `RAZORPAY_WEBHOOK_SECRET`

---
*Generated: 2026-02-12*

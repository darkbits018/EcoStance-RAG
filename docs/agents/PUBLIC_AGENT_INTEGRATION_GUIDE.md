# Public AI Agent Integration Guide

This guide provides a comprehensive manual for developers to integrate the **EcoStance Public Agent** into any external website or chat widget.

---

## 1. Overview
The Public Agent is designed for unauthenticated user interaction (anonymous visitors). It relies on a `session_id` to maintain conversation state and an `X-Tenant-ID` header to identify the organization.

## 2. API Reference

### Base URL
`http://<your-backend-api>/api/v1/public-agent`

### Endpoint: Initiate/Continue Chat
- **URL**: `POST /chat`
- **Headers**:
    - `Content-Type: application/json`
    - `X-Tenant-ID: <REQUIRED_TENANT_ID>`
- **Request Body**:
    ```json
    {
      "message": "User's message here",
      "session_id": "unique-client-side-id",
      "user_language": "en" 
    }
    ```

### Endpoint: Fetch Configuration
Use this to get branding colors, welcome messages, and suggested questions.
- **URL**: `GET /config`
- **Headers**:
    - `X-Tenant-ID: <REQUIRED_TENANT_ID>`

---

## 3. Implementation Workflow

### Step 1: Session Management
Generate a persistent `session_id` on the client-side (e.g., using `uuid` or a timestamp-random string combo). Store this in `localStorage` or `sessionStorage` so the conversation persists if the user refreshes the page.

### Step 2: Custom UI Rendering (The Component Protocol)
The agent doesn't just return text; it returns **structured logic**. Your widget must be able to handle different response types:

#### A. Text Response
If the agent returns a string, render a standard message bubble.

#### B. Impact Dashboard (`impact_stats`)
If the response contains `type: "impact_stats"`, render a visualization showing:
- CO2 Offset (tonnage)
- Trees Planted (count)
- Eco-Rank

#### C. Certificate Card (`certificate_card`)
If the response contains `type: "certificate_card"`, render a "High-End" widget with:
- Project ID
- Verification Status (Badge)
- Project Location

#### D. Product Gallery (`product_gallery`)
Render an interactive carousel or grid of products based on the items array returned.

### Step 3: Handling Language
The agent is multilingual. You can optionally send `user_language` in the request, or let the agent auto-detect and respond. The response will include a `language` field so you can adjust UI labels (like "Loading..." or "Send") accordingly.

---

## 4. Security & Rate Limiting
- **No JWT Required**: Since this is public-facing, you do not need an Authorization token.
- **Tenant Isolation**: Only resources (Knowledge Bases/Tools) explicitly assigned to your `Tenant ID` in the admin panel will be accessible.
- **Rate Limits**: By default, limited to **10 queries per minute** per session to prevent abuse.

---

## 5. Sample Integration Block (Javascript)

```javascript
const sendMessage = async (input) => {
  const response = await fetch('https://api.ecostance.com/api/v1/public-agent/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Tenant-ID': 'your-tenant-uuid-here'
    },
    body: JSON.stringify({
      message: input,
      session_id: getStoredSessionId()
    })
  });

  const data = await response.json();
  
  // Logic to handle rich components
  if (data.response.type === 'certificate_card') {
     renderCertificateWidget(data.response.data);
  } else {
     renderMessageBubble(data.response);
  }
};
```

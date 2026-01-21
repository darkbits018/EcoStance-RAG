# Final Specification: E-Commerce Agent & API Protocol

**Can we make a separate agent without redundant code?**
**YES.**

This document contains the complete specification, code implementation, and integration details for adding a dedicated E-Commerce Agent to your platform using the existing architecture.

---

## 1. Architecture: The "No Redundancy" Model

To avoid copying the entire ReAct logic, we define the Agent not as a new class, but as a **Configuration Profile**.
We reuse the core `AgentService` logic. We simply inject a different "Brain" (Prompt) and "Hands" (Tools) into it.

---

## 2. The Hybrid Response Protocol

To satisfy the requirement: *"Text for conversation, JSON for products/components"*, the API will strictly follow this response schema. This allows the Frontend to know exactly when to render a Bubble vs a Component.

**All responses from the backend `chat` endpoint will be a JSON Object.**

### Schema Structure
```typescript
interface AgentResponse {
  type: "text" | "product_list" | "url_action"; 
  message: string;        // The conversational part (e.g. "Here is what I found")
  data?: any;            // The structured payload for components
}
```

### Scenario A: Normal Conversation (Text Only)
**User:** "Hi, how are you?"
**Agent Response:**
```json
{
  "type": "text",
  "message": "I'm doing great! How can I help you shop today?",
  "data": null
}
```
*Frontend Behavior:* Render a standard chat text bubble.

### Scenario B: Product Search (Component)
**User:** "Show me some gaming headsets."
**Agent Response:** 
```json
{
  "type": "product_list",
  "message": "I found these top-rated gaming headsets for you:",
  "data": {
    "items": [
      {
        "id": 101,
        "name": "Sony Inzone H9",
        "price": 299.00,
        "image": "https://...",
        "slug": "sony-inzone"
      },
      {
        "id": 102,
        "name": "Logitech G Pro X",
        "price": 129.00,
        "image": "https://...",
        "slug": "logitech-g-pro"
      }
    ]
  }
}
```
*Frontend Behavior:* Render the `message` as text, then immediately below it, render the `<ProductCarousel />` component using the `data.items` array.

### Scenario C: Action/Link (Component)
**User:** "Where is my order?" (User not logged in)
**Agent Response:**
```json
{
  "type": "url_action",
  "message": "You need to be logged in to view your orders.",
  "data": {
    "url": "/login",
    "button_text": "Login Now"
  }
}
```
*Frontend Behavior:* Render text + a standard "Call to Action" button.

---

## 3. Agent "Brain" Configuration (System Prompt)

The System Prompt is the key to enforcing this behavior. We instruct the LLM to output a specific JSON structure when it finds data.

```python
ECOMMERCE_SYSTEM_PROMPT = """
You are the E-Commerce Shopping Assistant.
Your goal is to help customers find products and check their orders.

### RESPONSE FORMAT RULES
1. **Normal Chat**: If you are just talking, greeting, or explaining, answer normally.
   - Example: "Hi there! I can help you find electronics."

2. **Data Found**: If you use a tool (like `find_products`) and get results, you MUST return a JSON object strictly following this format:
   ```json
   {
     "type": "product_list",
     "message": "Brief text introduction here",
     "data": { "items": [ ...raw tool results... ] }
   }
   ```

3. **Links/Actions**: If the user needs to specific page (like login), return:
   ```json
   {
     "type": "url_action",
     "message": "Please log in first",
     "data": { "url": "/login", "button_text": "Log In" }
   }
   ```

### AVAILABLE TOOLS:
1. `find_products(search_term, category)`: Returns list of products.
2. `get_my_orders(user_id)`: Returns order history.

### BEHAVIOR:
- Do NOT list products in the `message` text field.
- Do NOT describe the price or details in text if you are returning the JSON card. Let the UI handle it.
- Keep the `message` short.
"""
```

---

## 4. Python Implementation (Tools)

Create `app/services/ecommerce_tools.py`.

```python
import requests
import json

BASE_URL = "http://localhost:3000/api"

def find_products(search: str = None, category_slug: str = None) -> list:
    """
    Search for products.
    Returns: Python List (not string) to be embedded in the final JSON response.
    """
    params = {}
    if search: params['search'] = search
    if category_slug: params['category'] = category_slug
    
    try:
        response = requests.get(f"{BASE_URL}/products", params=params)
        response.raise_for_status()
        return response.json() # Return actual list/dict, not string
    except:
        return []

def get_my_orders(user_id: str) -> list:
    """Get orders for valid user_id."""
    if not user_id: return []
    try:
        response = requests.get(f"{BASE_URL}/orders", params={"user_id": user_id})
        return response.json()
    except:
        return []
```

---

## 5. Security Note regarding Orders

**Requirement:** *"track customers order if they are logged in"*

1.  **Frontend**: Must send `Authorization: Bearer <token>` with the chat request.
2.  **Backend**:
    -   Middleware validates the Token.
    -   Extracts `user_id`.
    -   Passes `user_id` to the Agent Context.
3.  **Agent Tool**:
    -   `get_my_orders` checks if `user_id` is present.
    -   If valid, it calls the backend API.
    -   If invalid/null, the Agent returns the `url_action` JSON to prompt login.

## 6. Summary

-   **Frontend**: Looks for `type` in the response. If `text`, shows bubble. If `product_list`, shows Carousel.
-   **Backend**: Agent logic remains the same, but the **System Prompt** forces structured JSON output when specific tools are used.
-   **Integration**: Zero redundant code in the engine; custom logic is isolated in the Prompt and Toolset.

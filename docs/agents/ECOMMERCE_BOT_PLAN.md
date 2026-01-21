# E-Commerce Bot Integration Plan

## 1. Feasibility Analysis
**Can you add more agents without redundant code?**
**Yes.** The current architecture used in `quickship_agent` is designed with the ReAct pattern, which separates the "brain" (LLM) from the "body" (Tools). To add an E-commerce bot without redundancy, we will convert the existing specific `PublicAgentService` into a generic, configurable `AgentEngine` that can load different "Skills" (Tools + Prompts) based on the context.

**Capabilities Check:**
*   **Answer FAQs:** ✅ Fully supported via the existing `KnowledgeBase` tools (RAG).
*   **Custom Product Component:** ✅ Possible. The agent can be instructed to return structured JSON (e.g., `product_card`) which the frontend detects and renders as a UI component instead of plain text.
*   **Track Customer Orders:** ✅ Possible. We need to pass the "Authenticated User Context" (User ID) into the agent's session so the tools can query *their* specific orders securely.

---

## 2. Architecture Strategy

To avoid code duplication, we will refactor the hardcoded `quickship_agent` into a modular system:

### A. The Generic Agent Engine
Instead of `PublicAgentService` being hardcoded for shipping, we'll create a generic class that accepts:
1.  **System Prompt**: Defines the persona (e.g., "You are a helpful Shop Assistant...").
2.  **Tool Registry**: A list of allowed Python functions (e.g., `search_products`, `check_order`).
3.  **Context**: Session variables (User ID, Tenant ID).

### B. E-Commerce "Skill Pack"
We will define a specific configuration for the E-commerce bot:
*   **Tools**:
    *   `search_products(query, category)`: Returns product list.
    *   `get_product_details(product_id)`: Returns full specs.
    *   `get_my_orders(limit)`: Returns logged-in user's recent orders.
    *   `kb_search(query)`: (Existing) Answers FAQs like return policy, shipping times.
*   **Prompt**: Instructions to use the `search_products` tool when a user asks to "buy" or "see" items, and to use `kb_search` for policy questions.

---

## 3. Implementation Details

### Step 1: Define the Product Tools
Create a new file `app/services/ecommerce_tools.py` (or similar) containing the functions:
```python
def search_products(query: str, price_range: str = None):
    """
    Searches the product database.
    Returns: JSON list of products with image_url, price, name.
    """
    # ... database query implementation ...
    pass

def get_my_orders(user_id: str):
    """
    Fetches orders for the currently logged-in user.
    """
    # ... secure database query ...
    pass
```

### Step 2: Structured Responses for Custom UI
The "Wow" factor comes from the UI. The agent shouldn't just say "We have a blue shirt." It should return a data structure the frontend can render.

**System Prompt Instruction:**
> "When the user asks to see products, use the `search_products` tool. Do not summarize the output yourself. Instead, pass the raw tool output to the client so it can be rendered as a card."

**Response Format Contract:**
The API should return a structure like:
```json
{
  "type": "message",
  "content": "Here are some sneakers you might like:",
  "attachments": [
    {
      "type": "product_card_carousel",
      "data": [
        {"id": "123", "name": "Air Max", "price": 120, "image": "..."}
      ]
    }
  ]
}
```

### Step 3: Authentication Context
Currently, the `chat` endpoint might be public. For order tracking:
1.  The frontend must send an auth token with the request.
2.  The backend verifies the token and extracts the `user_id`.
3.  The `user_id` is passed into the `AgentService.chat(..., user_context={"user_id": 123})` method.
4.  The `get_my_orders` tool checks this `user_context`. If missing, the agent asks the user to log in.

---

## 4. Execution Roadmap

1.  **Refactor**: Rename/Abstract `quickship_agent` to `CoreAgentService`.
2.  **Create Tools**: Implement the e-commerce checking functions connected to your product DB.
3.  **Configure**: Create a new instantiation of the agent in `main.py` or a router specifically for the shop bot.
4.  **Frontend Update**: Update the chat component to handle `product_card` message types.

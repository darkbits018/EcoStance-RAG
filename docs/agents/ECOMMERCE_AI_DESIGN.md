# E-Commerce AI Agent Design
Based on API Documentation: `docs/agents/ecomm-api-doc.md`

## 1. Zero-Redundancy Architecture
To avoid rewriting the agent code for every new bot, we will use a **Configurable Agent Service**.
Instead of hardcoding tools inside the class, we pass them during initialization.

```python
# Conceptual generic agent structure
class GenericAgentService:
    def __init__(self, system_prompt: str, tools: List[Tool]):
        self.agent = create_react_agent(model, tools, system_prompt)
        
    def chat(self, user_input, context):
        return self.agent.invoke(user_input, context)
```

## 2. Tool Definitions (The "Skills")
The AI needs "Function Calling" definitions to interact with your Express.js API.

### Tool A: `find_products`
**Purpose**: Allows the AI to search for items or filter by category.
- **Python Wrapper**:
  ```python
  def find_products(search_term: str = None, category_slug: str = None) -> str:
      """
      Search for products by name or category.
      Args:
          search_term: The product name to look for (e.g., "headphones")
          category_slug: The category to filter by (e.g., "audio", "gaming")
      """
      params = {}
      if search_term: params['search'] = search_term
      if category_slug: params['category'] = category_slug
      
      # Calls your Node API
      response = requests.get("http://localhost:3000/api/products", params=params)
      return json.dumps(response.json())
  ```

### Tool B: `get_all_categories`
**Purpose**: Helps the AI understand what *kinds* of items are sold when the user asks vague questions like "what do you sell?".
- **Python Wrapper**:
  ```python
  def get_all_categories() -> str:
      """Returns list of available product categories."""
      response = requests.get("http://localhost:3000/api/categories")
      return json.dumps(response.json())
  ```

### Tool C: `get_customer_orders` (Gap Analysis)
**Requirement**: You mentioned *'track customers order'*.
**Gap**: Your `ecomm-api-doc.md` does **not** list an Order endpoint.
**Proposed Tool**:
```python
def get_my_orders(user_id: str) -> str:
    """
    Fetches orders for the designated user.
    Note: Requires backend API endpoint `GET /api/orders?user_id=...`
    """
    if not user_id:
        return "Error: User not logged in."
    
    response = requests.get(f"http://localhost:3000/api/orders/user/{user_id}")
    return json.dumps(response.json())
```

## 3. The Brain (System Prompt)
This is the "Configuration" that makes the generic agent act like a Shop Assistant.

```text
You are an intelligent Shopping Assistant for an electronics store.

RULES:
1. When asked about products, ALWAYS use the `find_products` tool. Do not guess.
2. If a user asks broadly "what do you have?", use `get_all_categories` first to show range.
3. If a user asks "Where is my order?", check if you have a `user_id` in your context. 
   - If yes, use `get_my_orders`.
   - If no, politely ask them to sign in.
4. FORMATTING:
   - When listing products, be brief.
   - If you find products, the system will render them visually. You just need to return the data.

CAPABILITIES:
- Search: "Show me sony headphones" -> find_products(search_term="sony", category_slug="audio")
- Browsing: "Do you sell cameras?" -> find_products(category_slug="photography")
```

## 4. Integration Workflow

1.  **User Request**: "Show me gaming stuff"
2.  **Agent Logic**:
    *   Analyzes constraints.
    *   Decides to call `find_products(category_slug="gaming")`.
3.  **Tool Execution**:
    *   Python calls `GET http://localhost:3000/api/products?category=gaming`
    *   Receives JSON list of PS5, Xbox, etc.
4.  **Response Generation**:
    *   Agent summarizes: "I found some great gaming gear for you."
    *   **Crucial Step**: The agent returns the JSON array of products in a structured field so the UI renders the "Custom Component" you asked for.

## summary
You can achieve your goal by creating a **single Generic Agent** class in Python, and instantiating it with these specific tools that wrapper your Node.js API. No new complex logic is needed, just new Tool Definitions.

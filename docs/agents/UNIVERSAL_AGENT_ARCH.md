# Universal Multi-Tenant Agent Architecture

## Problem Analysis
Currently, `public_agent_router.py` hard-imports `quickship_agent.public_agent_service`. This creates a dependency where every tenant is forced to be a "QuickShip" tenant. 
To support E-Commerce, Real Estate, or generic users without writing new Routers or Frontends, we need a **Dynamic Injection System**.

## 1. The Solution: "Plugins, not Agents"

Instead of `EcommerceAgent` vs `QuickshipAgent`, we will have **One Universal Agent Service**.
This service initializes itself by looking at the Tenant's Configuration and loading the appropriate **Tool Plugins**.

### Architecture Diagram

```mermaid
graph TD
    Router[Public Agent Router] --> Factory[Agent Factory]
    Factory -->|Read Config| DB[(Tenant DB)]
    
    DB -->|Tools=['product_search']| EComm[E-Commerce Tenant]
    DB -->|Tools=['shipment_track']| Logist[Logistics Tenant]
    
    Factory -->|Load Tools| UniversalAgent
    UniversalAgent -->|Equipped with| Plugin1[Product Tool]
    UniversalAgent -->|Equipped with| Plugin2[Tracking Tool]
    
    UniversalAgent -->|JSON Protocol| Frontend
```

## 2. Server-Driven UI (Frontend Solved)

You concerned: *"I cant be making custom frontend for all"*.
**Solution:** The backend dictates the UI using a Standardized Component Protocol.

The Frontend only needs **ONE** smart component: `<DynamicAgentResponse />`.

**Protocol Schema:**
```json
{
  "component": "card_carousel",
  "title": "Found Items",
  "data": [
    { "title": "PS5", "image": "...", "subtitle": "$499", "action_payload": "id_123" }
  ]
}
```

If you add a Real Estate agent later, you just return:
```json
{
  "component": "card_carousel",
  "title": "Luxury Condos",
  "data": [ ...house data... ]
}
```
**The Frontend code does not change.** It just renders cards with different text.

## 3. Implementation Steps

### A. Create the Tool Registry
Move all tools to `app/agent_modules/`.
*   `app/agent_modules/ecommerce/tools.py`
*   `app/agent_modules/logistics/tools.py`

### B. The `AgentFactory`
Update `app/services/agent_factory.py`:
```python
def create_agent_for_tenant(tenant_id: str):
    config = get_tenant_config(tenant_id)
    allowed_tools_names = config.allowed_tools # e.g. ["ecommerce_basic", "logistics_tracking"]
    
    tools = []
    for name in allowed_tools_names:
        tools.extend(load_tool_module(name))
        
    return UniversalAgent(tools=tools, system_prompt=config.custom_prompt)
```

### C. Refactor `PublicAgentRouter`
Change the import:
```python
# OLD
from quickship_agent.public_agent_service import PublicAgentService

# NEW
from app.services.agent_factory import get_agent_service
agent = get_agent_service(tenant_id)
```

## 4. Why this works
1.  **Multi-Tenant**: Each tenant selects their "Skill Pack" in the Admin Panel.
2.  **No Redundant Code**: One Agent Class handles logic (RAG, Conversation, History).
3.  **No Custom Frontend**: The JSON Protocol ensures the UI remains generic (Cards, Lists, Key-Value Pairs).

This transforms your system from a "Shipping Bot" to a "Universal Business Bot Platform".

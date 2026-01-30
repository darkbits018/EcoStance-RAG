# How the System Knows Which Agent to Use

The system uses a **Configuration-Driven Approach**. 
There isn't a hard link saying "Tenant X uses Class Y". Instead, there is a configuration row in the database that defines the **Capabilities (Skills)** of the agent for that tenant.

## 1. The Database Record (`public_agent_configs`)

Every tenant has exactly one row in the `public_agent_configs` table. This row contains the "DNA" of their agent.

### Example: E-Commerce Tenant
**Tenant ID:** `tenant_123_shop`
```json
{
  "allowed_tools": ["product_search", "order_history", "category_list"],
  "system_prompt_override": "You are a helpful Shop Assistant...",
  "branding": { "name": "MegaStore" }
}
```

### Example: Logistics Tenant
**Tenant ID:** `tenant_456_ship`
```json
{
  "allowed_tools": ["shipment_tracking", "delivery_estimate"],
  "system_prompt_override": "You are a Logistics Expert...",
  "branding": { "name": "QuickShip" }
}
```

## 2. The Runtime Logic (How it works)

When a user sends a chat message:

1.  **Identify Tenant**: The API receives the request `POST /api/chat` and extracts `Tenant-ID` from the header or subdomai


n.
2.  **Fetch Config**: The system queries the DB: `SELECT * FROM public_agent_configs WHERE tenant_id = '...'`.
3.  **Assemble Agent**: The **AgentFactory** reads the `allowed_tools` array from the result.
    *   If it sees `"product_search"`, it imports `ecommerce_agent.tools.find_products`.
    *   If it sees `"shipment_tracking"`, it imports `quickship_agent.tools.track_shipment`.
4.  **Launch**: The Agent is spun up in milliseconds with *only* those specific tools available.

## 3. How You (The Admin) Control It

You don't write code to switch agents. You toggle features in the **Admin Panel**.

*   **API Endpoint**: `PUT /api/v1/admin/public-agent/config`
*   **Payload**:
    ```json
    {
      "enabled": true,
      "allowed_tools": ["product_search", "order_history"] 
    }
    ```

## Summary
The "Integration" is defined by the **List of Tools** allowed in the database. 
*   **Tenant A** = Agent Engine + [Shop Tools]
*   **Tenant B** = Agent Engine + [Shipping Tools]
*   **Tenant C** = Agent Engine + [Real Estate Tools]

They all use the **same source code** (`UniversalAgentService`), but behave completely differently because they are fed different tools and prompts.

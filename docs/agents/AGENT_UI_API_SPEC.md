# AI Agent Interaction & API Specification

This document details the interface between the **EcoStance AI Backend** and the **Frontend**, focusing on the specialized agent behaviors and the component-based response protocol.

## 1. API Architecture

The system uses a unified orchestration layer to handle different agent types. All public-facing AI interactions are consolidated into a single endpoint set.

### Public Chat Endpoint
- **URL**: `POST /api/v1/public-agent/chat`
- **Purpose**: Unified entry point for all customer-facing agents.
- **Request Parameters**:
    - `session_id`: Unique identifier for the conversation session.
    - `message`: User input string.
    - `agent_type`: (Optional) Override for the tenant's default agent (`quickship`, `ecommerce`, `ecostance`, `generic`).
    - `user_language`: (Optional) Force a specific response language.

### Configuration Management (Tenant Admin)
- **URL**: `PUT /api/v1/admin/public-agent/config`
- **Purpose**: Admin-only endpoint to define which agent persona a tenant uses.

### Global Configuration Management (SuperAdmin)
- **URL**: `PUT /api/v1/superadmin/public-agent/config/{tenant_id}`
- **Purpose**: SuperAdmin-only endpoint to assign agents or modify configuration for ANY tenant.
- **Key Fields**:
    - `agent_type`: Defines the logic core (e.g., `ecostance`, `ecommerce`, `quickship`).
    - `allowed_tools`: Enables specific capabilities (e.g., `certificates`, `impact`, `shopping`, `tracking`).
    - `branding`: Controls UI colors and logos for the chat widget.

---

## 2. Response Protocol (Component-Based UI)

The backend has transitioned from plain-text responses to a **JSON-Rich Protocol**. This allows the frontend to render high-fidelity, interactive components instead of message bubbles.

### Response Structure
Responses now follow a standard object structure:
- `response`: A JSON object (or text) containing the interaction logic.
- `session_id`: Persisted session ID.
- `language`: Detected or preferred response language.

### UI Component Types

#### A. Certificate Card (`certificate_card`)
- **Agent**: EcoStance
- **Details**: Used for carbon offset verification. Contains project name, verification status, issuance date, and total tonnage.

#### B. Product Gallery (`product_gallery` / `product_list`)
- **Agents**: EcoStance, Ecommerce
- **Details**: Displays an interactive carousel of merchandise. Includes product names, images, prices, and sustainability "Eco-Ratings" (exclusive to EcoStance).

#### C. Impact Dashboard (`impact_stats`)
- **Agent**: EcoStance
- **Details**: Displays a summary of the user's environmental contribution, trees planted equivalent, and achievement rankings.

#### D. Action Links (`url_action`)
- **Agent**: Ecommerce
- **Details**: Triggers a button within the chat that redirects users to specific pages (e.g., Login, Cart, or Registration).

---

## 3. Organizational Changes

To support this diversity of agents, the backend has been restructured:
- All agent logic is now encapsulated within the `agents/` root directory.
- Each agent (`quickship`, `ecommerce`, `ecostance`) maintains its own configuration, toolset, and system prompts.
- A shared `MultilingualAgentMixin` ensures language consistency across all specialized personas.

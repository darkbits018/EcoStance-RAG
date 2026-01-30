# EcoStance Agent V1 - Feature & Status Master List

This document provides a comprehensive report of all features implemented in the codebase, as well as an assessment of partially completed or missing functionality based strictly on the current code state.

## 1. Core Multi-Tenant Infrastructure
*   **Hosted Multi-Tenancy**: Centralized PostgreSQL database (hosted on Aiven) with strict tenant isolation via `tenant_id` filters in all queries.
*   **Identity & Access (RBAC)**:
    *   System Roles: `super_admin`, `tenant_admin`, and standard `user`.
    *   JWT-based authentication with token refresh logic.
    *   Permission-based routing in FastAPI.
*   **Database Management**:
    *   Dynamic connection pooling and statistic tracking.
    *   Support for both hosted PostgreSQL and local SQLite (for specific agent data).
    *   Automatic schema migrations for configuration improvements (e.g., `agent_type` injection).

## 2. Public Agent Ecosystem
*   **Universal Agent Framework**: A modular architecture that selects an agent "personality" and "skill-set" based on the tenant's configuration.
*   **Multi-Agent Types**:
    *   **QuickShip Agent**: Specialized logistics expert with tools for tracking, payment status (COD), delivery estimates, and complaint resolution.
    *   **E-commerce Agent**: Shopping assistant with product search, category browsing, and order tracking via external Node.js API integration.
    *   **Generic Agent (Default)**: Lean fallback agent that only utilizes RAG (search knowledge base) and raw SQL database queries.
*   **Hybrid Response Protocol**: Backend support for rich UI components. Agents can return:
    *   `text`: Standard conversation.
    *   `product_list`: Structured data for carousels.
    *   `url_action`: Call-to-action buttons (e.g., "Log In", "Check Status").
*   **Admin Console Back-end**:
    *   Configuration for branding (logo, colors), rate limits, and welcome messages.
    *   Tool toggle system (enable/disable specific skill sets per tenant).

## 3. Knowledge Base & RAG (Retrieval-Augmented Generation)
*   **Vector Database (Qdrant)**: Full integration for high-performance semantic search.
*   **File Processing Pipeline**:
    *   Support for 15+ file formats including PDF, Docx, and EML.
    *   **OCR Integration**: Tesseract-based extraction for images and scanned documents.
    *   **Audio RAG**: Support for transcribing and searching audio files.
*   **Contextual Search**: Tenant-isolated collections in Qdrant ensuring one company's data never leaks to another.

## 4. Third-Party Integrations
*   **Gmail Integration**:
    *   OAuth2 flow for tenant users.
    *   Background syncing of email threads into the RAG system.
    *   Tool for agents to search and summarize user emails.
*   **CRM Modules**:
    *   **Custom CRM**: Logic for fetching and indexing custom customer data.
    *   **MS Dynamics**: Auth and fetch services for Dynamics 365.
*   **Scheduler Service**: Background task management for keeping external data (Emails, CRM records) in sync with the RAG vector store.

---

## 5. Partially Done / Missing Features (Code Analysis)

### 🔴 Missing / Not Functional
*   **Analytics Visualization Data**: The `/analytics` endpoint in `public_agent_router.py` returns empty lists for `usage_by_day` and hardcoded zeros for `rate_limit_hits`. The data is collected in the DB but the aggregation logic for the time-series response is missing.
*   **Generic Agent Schema Mapping**: While the Generic Agent has a `query_database` tool, there is currently no mechanism to provide the database schema (Table names/Columns) to the LLM. It currently relies on the LLM "guessing" or the user describing the schema.
*   **E-commerce Order Data**: The `get_my_orders` tool is implemented to call `/api/orders`, but the corresponding Node.js endpoint is noted in the spec as missing/dummy.

### 🟡 Partially Done (Placeholders Exist)
*   **Salesforce Integration**: While several "CRM" services exist, they are primarily wrappers around generic fetch logic. A deep, field-mapped Salesforce integration is outlined in plans but only partially represented in `custom_crm_rag_service.py`.
*   **Cache Invalidation**: The `cache_router.py` exists, but many service methods do not yet implement the `CACHE_INVALIDATE_ON_KB_UPDATE` logic mentioned in the `.env`.
*   **Rate Limit Enforcement**: Global rate limiting exists, but the granular "Queries Per Minute" per tenant defined in `public_agent.py` models is not fully enforced across all legacy chat endpoints.

### 🟢 Tech Debt / Clean-up Needed
*   **Database Redundancy**: Some services still have `sqlite3` imports hardcoded while the primary system has moved to hosted PostgreSQL.
*   **Manual Scripts**: Several maintenance tasks (like restricting tenant tools) are currently handled by standalone Python scripts in `/scripts` rather than an integrated Admin UI.

# Salesforce Integration Plan

## 1. Overview
Integrate Salesforce to ingest Leads, Contacts, Opportunities, and associated activities (Emails, Tasks) into the EcoStance RAG system.

## 2. Architecture
Follow the established pattern:
- **`app/services/salesforce_fetch_service.py`**: Connects to Salesforce API.
- **`app/services/salesforce_rag_service.py`**: Processes data into Qdrant.
- **`app/routers/salesforce_router.py`**: API endpoints.

## 3. Technology Stack
- **Library**: `simple-salesforce` (Official-like Python client).
- **Auth**: OAuth2 (Web Server flow) or Username/Password + Security Token.
- **Database**: Add `SalesforceConfig` to `Tenant` model to store credentials/tokens.

## 4. Key Features
- **Ingestion**:
    - **Objects**: Leads, Contacts, Opportunities, Accounts.
    - **Activities**: Emails, Calls, Notes linked to unique IDs.
- **Sync**:
    - Manual Trigger.
    - Scheduled Background Sync.
- **RAG**:
    - Create embeddings for notes and email bodies is critical.
    - Structured fields (Status, Amount) stored as metadata for filtering.

## 5. Implementation Steps
1.  Add `simple-salesforce` to `requirements.txt`.
2.  Create `app/services/salesforce_auth_service.py` to handle OAuth flow.
3.  Create Fetch Service to query SOQL (Salesforce Object Query Language).
4.  Create RAG Service (Reuse chunking logic).
5.  Add Router & Permissions.
6.  Frontend: Add "Connect Salesforce" card.

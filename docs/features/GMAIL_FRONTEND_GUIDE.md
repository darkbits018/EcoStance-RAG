# Gmail Integration - Frontend Implementation Guide

This document outlines the API endpoints, data structures, and UI requirements for implementing the Gmail Integration feature in the frontend.

## 1. Feature Overview
The Gmail Integration allows tenants to:
1.  **Connect their Gmail account** via OAuth.
2.  **Manage Recipients**: Specify which email addresses to fetch emails from.
3.  **Manage Schedules**: Configure how often to sync emails.
4.  **RAG Automation**: Fetched emails are automatically processed into the tenant's Knowledge Base.

## 2. API Endpoints

### A. Authentication (OAuth)
**Goal**: Connect the tenant's Google Workspace/Gmail account.

*   **Step 1: Get Auth URL**
    *   **Endpoint**: `GET /api/v1/gmail/auth`
    *   **Response**: `{ "auth_url": "https://accounts.google.com/..." }`
    *   **Action**: Redirect the user's browser to this URL.

*   **Step 2: Handle Callback**
    *   **Route**: Creating a frontend route `/gmail/callback` (or similar) to handle the redirect from Google.
    *   **Params**: Google will redirect with `?code=...` and `&state=...`.
    *   **Endpoint**: `POST /api/v1/gmail/callback`
    *   **Body**: `{ "code": "4/0A..." }`
    *   **Response**: `{ "message": "Successfully connected...", "email": "user@example.com" }`

### B. Recipient Management
**Goal**: List and add email addresses to monitor.

*   **List Recipients**
    *   **Endpoint**: `GET /api/v1/gmail/recipients`
    *   **Response**: `[ { "id": "...", "email_address": "...", "enabled": true, ... } ]`

*   **Add Recipient**
    *   **Endpoint**: `POST /api/v1/gmail/recipients`
    *   **Body**:
        ```json
        {
          "email_address": "client@example.com",
          "display_name": "Client X",
          "group_name": "Sales",
          "enabled": true
        }
        ```

*   **Remove Recipient**
    *   **Endpoint**: `DELETE /api/v1/gmail/recipients/{id}`

### C. Schedule Management
**Goal**: Configure when the sync runs.

*   **List Schedules**
    *   **Endpoint**: `GET /api/v1/gmail/schedules`
    *   **Response**: `[ { "id": "...", "name": "Daily Sync", "next_run": "...", ... } ]`

*   **Create Schedule**
    *   **Endpoint**: `POST /api/v1/gmail/schedules`
    *   **Body**:
        ```json
        {
          "name": "Hourly Check",
          "schedule_type": "interval",
          "schedule_config": { "minutes": 60 },
          "recipient_ids": ["uuid-1", "uuid-2"],
          "enabled": true
        }
        ```
    *   **Note**: `recipient_ids` is a list of IDs from the Recipient API.

### D. Sync Operations & History
**Goal**: Trigger manual syncs and view ingested emails.

*   **Manual Sync**
    *   **Endpoint**: `POST /api/v1/gmail/schedules/{schedule_id}/sync`
    *   **Body**: `{}` (Empty JSON)
    *   **Action**: Immediately runs the sync task. Show a loading spinner.

*   **List Ingested Messages**
    *   **Endpoint**: `GET /api/v1/gmail/messages?limit=50&offset=0`
    *   **Response**:
        ```json
        [
          {
            "id": "uuid",
            "gmail_message_id": "19b9...",
            "subject": "Project Update",
            "sender": "client@example.com",
            "snippet": "Hello, here is the update...",
            "received_at": "2026-01-06T12:00:00",
            "ingested_at": "2026-01-06T14:30:00"
          }
        ]
        ```

*   **Delete Message**
    *   **Endpoint**: `DELETE /api/v1/gmail/messages/{id}`
    *   **Action**: Deletes the message record and removes its RAG vectors from the system.
    *   **Response**: `{ "message": "Message and vectors deleted successfully" }`

## 3. UI/UX Requirements

### 1. Gmail Settings Page
*   **Location**: Tenant Settings > Integrations > Gmail.
*   **Connection Status**:
    *   Show "Connect Gmail" button if not connected.
    *   Show "Connected as user@example.com" (green badge) if connected.
    *   *Note: You might need to fetch tenant settings to check current connectivity status (currently usually stored in `gmail_config` on the backend).*

### 2. Recipient Table
*   **Columns**: Email Address, Name, Group, Status (Enabled/Disabled), Actions (Delete).
*   **Add Button**: Opens a modal to input email and name.

### 3. Schedule Configuration
*   **Layout**: A card or section showing active schedules.
*   **Inputs**:
    *   Name (Text)
    *   Type (Dropdown: Interval, Daily)
    *   Frequency (Number input for minutes if Interval).
    *   Recipients (Multi-select dropdown).

### 4. History Table
*   **Goal**: Show users what has been successfully ingested.
*   **Columns**: Subject, Sender, Snippet, Received Date, Ingested Date.
*   **Pagination**: Simple Previous/Next buttons using `offset`.

## 4. Permissions & Error Handling
*   **Permissions**:
    *   `GMAIL_CONFIGURE`: Needed for OAuth.
    *   `GMAIL_MANAGE_RECIPIENTS`: Needed for adding/removing emails.
*   **Errors**:
    *   `403 Forbidden`: User doesn't have permission. Show "Contact Admin".
    *   `400 Bad Request`: Invalid email format or missing fields.

## 5. Development Tips
*   **Testing OAuth**: Since the backend runs on `localhost:8000` and frontend on `localhost:5173`, ensure the Google Cloud Console redirect URIs are configured to match your frontend callback route.
*   **Mocking**: If you can't connect a real Google account yet, mock the API responses for the `GET /recipients` endpoints to build the table UI first.

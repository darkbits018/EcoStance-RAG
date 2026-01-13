# Dynamics 365 Integration - Frontend Implementation Guide

This document outlines the steps and API endpoints required to implement the Dynamics 365 configuration interface in the frontend.

## Overview
The goal is to allow Tenant Admins to connect their Microsoft Dynamics 365 (CRM) environment to the bot using a "Client Credentials" flow. This ensures the bot only accesses data explicitly tracked in CRM, rather than direct user mailboxes.

## 1. Permission Requirements
User must have the `DYNAMICS_CONFIGURE` permission (usually Tenant Admin role).
Hide the configuration UI if the user does not have this permission.

## 2. Configuration Page Design
Create a new settings page or tab under "Integrations" -> "Dynamics 365".

### Status Section
- **Check Status**: On load, call `GET /api/v1/dynamics/config`.
- **Display**:
    - If `is_configured: false`: Show "Not Connected" badge (Grey/Red).
    - If `is_configured: true`: Show "Connected" badge (Green).
    - Show `resource_url` if available.

### Configuration Form
Fields required to connect:

| Field Label | Key | Type | Description |
| :--- | :--- | :--- | :--- |
| **Azure Tenant ID** | `tenant_id` | Text | The Directory ID of the Azure AD. |
| **Client ID** | `client_id` | Text | The Application ID from App Registration. |
| **Client Secret** | `client_secret` | Password | The secret key (value) from App Registration. |
| **CRM URL** | `resource_url` | URL | The full URL of the Dynamics instance (e.g., `https://org123.crm.dynamics.com`). |

> **Note**: Add a "Test Connection" button next to "Save".

## 3. API Integration

### A. Get Current Configuration
**Endpoint**: `GET /api/v1/dynamics/config`
**Response**:
```json
{
  "tenant_id": "804...",
  "client_id": "a1b...",
  "resource_url": "https://org.crm.dynamics.com",
  "is_configured": true,
  "last_sync": null
}
```

### B. Save Configuration
**Endpoint**: `POST /api/v1/dynamics/config`
**Payload**:
```json
{
  "tenant_id": "uuid-string...",
  "client_id": "uuid-string...",
  "client_secret": "secret-value...",
  "resource_url": "https://org.crm.dynamics.com"
}
```

### C. Test Connection
**Endpoint**: `POST /api/v1/dynamics/test`
**Description**: Tries to authenticate and fetch 1 email to verify everything works.
**Response**:
```json
{
  "success": true,
  "message": "Successfully connected. Found 5 recent emails."
}
```
**UI Behavior**: Show a toast notification with the message. If success, enable the "Sync Now" button.

### D. Manual Sync (Sync Now)
**Endpoint**: `POST /api/v1/dynamics/sync/now`
**Query Param**: `?lookback_minutes=60` (optional, default 60)
**Response**:
```json
{
  "message": "Sync completed successfully",
  "emails_found": 12,
  "chunks_created": 24
}
```

## 4. User Workflow / UX

1. **Initial State**: User visits page. `GET` returns `is_configured: false`. Form is empty.
2. **Setup**: User enters credentials provided by their IT department.
3. **Validation**: User clicks "Test Connection". 
    - Frontend calls `POST /test`.
    - If error, show red alert: "Connection failed: [Error Message]".
    - If success, show green toast: "Connection Successful".
4. **Save**: User clicks "Save Configuration".
    - Frontend calls `POST /config`.
    - UI updates to "Connected" state.
5. **Sync**: User clicks "Sync Now".
    - Frontend calls `POST /sync/now`.
    - Show a loading spinner.
    - Display result: "Processed X new emails from CRM".

## 5. Security Notes
- Never display the `client_secret` back to the user after saving. The `GET` endpoint intentionally hides it.
- Ensure the `resource_url` is a valid HTTPS URL.

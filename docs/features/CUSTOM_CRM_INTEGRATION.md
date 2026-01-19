# Custom CRM Integration Guide

This document outlines the integration of the Custom CRM with the EcoStance Agent RAG system.

## 1. Overview

The integration allows EcoStance to ingest emails from a Custom CRM backend.
- **Source**: Custom CRM API (running locally).
- **Destination**: EcoStance Qdrant Vector Database (dedicated collection).
- **Features**: Manual Sync triggering, Duplicate prevention, and History viewing.

## 2. API Endpoints (Backend)

The following endpoints are available under the `/api/v1/custom-crm` prefix in the EcoStance Backend.

### 2.1 Trigger Sync
*   **Method**: `POST`
*   **Endpoint**: `/api/v1/custom-crm/sync`
*   **Description**: Initiates a background task to fetch emails from the CRM and process them into the RAG system.
*   **Authentication**: Requires a valid Tenant User token.
*   **Response**: Returns a success message indicating the sync has started in the background.

### 2.2 List Synced Emails
*   **Method**: `GET`
*   **Endpoint**: `/api/v1/custom-crm/emails`
*   **Description**: Returns a list of emails that have been successfully ingested into EcoStance.
*   **Parameters**: specific limits can be applied to control the number of records returned.
*   **Response**: Returns a list of objects containing the Internal ID, Original CRM ID, Subject, Sender, and Received Date.

---

## 3. Frontend Implementation Guide

To integrate this into the frontend application, you need to add a UI interface for managing this connection.

### 3.1 Recommended UI Structure

We suggest adding a **"Custom CRM"** tab or card within the **Integrations** or **Knowledge Base** section of your settings.

**Key Components:**

1.  **Sync Control**:
    - A **"Sync Now" button** to manually trigger the ingestion process.
    - Should include a **loading indicator** while the request is being processed.
    - Display a **success notification** (toast) once the background task is triggered.

2.  **Synced Data Table**:
    - A table displaying the history of ingested emails to provide visibility to the user.
    - Recommended Columns: `Subject`, `Sender`, `Received Date`.

### 3.2 logic Flow

**API Service Layer**:
- Create functions to interact with the two endpoints defined above.
- One function should handle the POST request to trigger the sync.
- Another function should handle the GET request to fetch the history.

**Component Logic**:
- On component mount, fetch the list of synced emails to populate the table.
- When the **Sync Now** button is clicked:
    1.  Set the UI to a "loading" state.
    2.  Call the sync endpoint.
    3.  On success, show a notification.
    4.  Optionally, wait a few seconds and refresh the list (or poll) to show the newly added emails in the table.
    5.  Reset the loading state.

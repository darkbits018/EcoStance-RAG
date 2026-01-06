# Gmail RAG Automation - Implementation Plan

This document outlines the specific coding tasks required to implement the Gmail Integration feature.

## Phase 1: Database & Models (Foundation)
**Goal**: Create schemas to store gmail configurations, recipients, and logs.

- [x] **Task 1.1**: Create `app/models/gmail.py`
    - Define `GmailRecipient` model (email, name, filters, tenant_id).
    - Define `GmailSchedule` model (schedule_config, type, enabled).
    - Define `GmailExecutionLog` model (status, emails_processed, errors).
- [x] **Task 1.2**: Update `app/models/tenant.py`
    - Add `gmail_config` JSON column for storing OAuth info (encrypted) and general settings.
- [x] **Task 1.3**: Database Migration
    - Create a migration script (e.g., `scripts/migrations/0add_gmail_tables.py`) to create new tables and update tenants table.
    - Run the migration.

## Phase 2: Gmail Service & OAuth (Connectivity)
**Goal**: Connect to Google APIs and fetch emails.

- [x] **Task 2.1**: Implement `app/services/gmail_auth_service.py`
    - Functions to generate OAuth authorization URL.
    - Functions to exchange code for tokens.
    - Functions to refresh tokens and store them securely in `VaultService` or `Tenant.gmail_config`.
- [x] **Task 2.2**: Implement `app/services/gmail_fetch_service.py`
    - Implement `GmailClient` wrapper around `google-api-python-client`.
    - Function `fetch_emails(recipient_email, filters)`: Search and retrieve raw messages.
    - Function `parse_email(raw_message)`: Extract body, subject, attachments.

## Phase 3: API Endpoints (Management)
**Goal**: Allow frontend/users to configure the system.

- [x] **Task 3.1**: Create `app/schemas/gmail.py`
    - Pydantic models for Requests/Responses (RecipientCreate, ScheduleUpdate, etc.).
- [x] **Task 3.2**: Create `app/routers/gmail_router.py`
    - `POST /config/auth`: Start OAuth flow.
    - `GET /recipients`: List monitored emails.
    - `POST /recipients`: Add new recipient.
    - `GET /schedules`: View sync schedules.

## Phase 4: RAG Integration & Scheduling (Automation)
**Goal**: Process emails into vectors and run automatically.

- [x] **Task 4.1**: Implement `app/services/gmail_rag_service.py`
    - Function `process_emails_to_kb(emails, tenant_id)`:
        - Chunk email content.
        - Generate embeddings (using existing EmbeddingService).
        - Upsert to Qdrant (using existing QdrantService).
- [x] **Task 4.2**: Update `app/services/scheduler_service.py`
    - Add `check_gmail_schedules()` job.
    - Logic to trigger `fetch_emails` -> `process_emails_to_kb` pipeline.

## Phase 5: UI Integration (Frontend)
- [ ] **Task 5.1**: Create Gmail Settings Page.
- [ ] **Task 5.2**: Add "Connect Gmail" button (OAuth).
- [ ] **Task 5.3**: Create Recipient Management Table.

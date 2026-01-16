# Backend Implementation Plan - Custom CRM (Gmail Dump)

## 1. Project Overview
The goal is to build a FastAPI backend for a Custom CRM that connects to Gmail, fetches emails based on specific criteria (recipients, labels), stores them ("dumps"), and allows for exporting and viewing.

## 2. Tech Stack
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: SQLModel (SQLite for local dev, PostgreSQL ready)
- **Gmail Integration**: `google-api-python-client`, `google-auth-oauthlib`
- **Async Tasks**: `BackgroundTasks` (FastAPI native) or Celery (future scaling)
- **Settings Management**: `pydantic-settings`

## 3. Directory Structure
```
c-crm-be/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── core/
│   │   ├── config.py        # Env vars (Client ID, Secret, Database URL)
│   │   ├── database.py      # DB session setup
│   │   └── security.py      # Encryption for tokens
│   ├── models/
│   │   ├── email.py         # Email and Attachment models
│   │   └── connection.py    # GmailConnection model (stores tokens)
│   ├── services/
│   │   ├── gmail_service.py # Gmail API interactions
│   │   └── dump_service.py  # Logic to process and save emails
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py  # OAuth flow endpoints
│   │   │   │   ├── dumps.py # Triggering dumps, status
│   │   │   │   └── emails.py# Reading emails (for UI)
│   │   │   └── api.py
│   └── schemas/             # Pydantic models for Req/Res
│       ├── email.py
│       └── dump.py
├── .env
├── requirements.txt
└── backend_implementation_plan.md
```

## 4. Key Components

### 4.1. Database Models (SQLModel)
- **GmailConnection**
    - `id`: UUID
    - `email_address`: String (Unique)
    - `access_token`: String (Encrypted)
    - `refresh_token`: String (Encrypted)
    - `token_expiry`: DateTime
    - `is_active`: Boolean

- **EmailDumpTask** (Tracks the fetching process)
    - `id`: UUID
    - `connection_id`: FK
    - `status`: Enum (PENDING, PROCESSING, COMPLETED, FAILED)
    - `criteria_type`: Enum (LABEL, RECIPIENT)
    - `criteria_value`: String (e.g., "INBOX", "client@example.com")
    - `started_at`: DateTime
    - `completed_at`: DateTime
    - `total_emails`: Integer

- **Email** (The dumped content)
    - `id`: String (Gmail Message ID, PK)
    - `thread_id`: String
    - `dump_task_id`: FK (Optional, or Many-to-Many if emails can belong to multiple dumps)
    - `sender`: String
    - `recipients`: String (JSON or comma-separated)
    - `subject`: String
    - `snippet`: String
    - `body_text`: Text
    - `body_html`: Text
    - `received_at`: DateTime
    - `labels`: JSON (List of strings)

### 4.2. Gmail Integration Service
- **Authentication**:
    - Use `Flow` from `google_auth_oauthlib.flow` to handle the OAuth2 dance.
    - Scopes: `https://www.googleapis.com/auth/gmail.readonly` (Minimum required).
- **Fetching**:
    - `users().messages().list`: To find IDs based on query (`q="to:recipient@example.com"` or `labelIds=["LABEL_ID"]`).
    - `users().messages().get`: To fetch full content.
    - **Optimization**: Use `batch` requests or async calls to improve speed.

### 4.3. Dump Logic
1.  User initiates dump via API.
2.  Backend creates an `EmailDumpTask` with status `PENDING`.
3.  Background Task starts:
    - Refresh OAuth token if needed.
    - Construct Gmail query from criteria.
    - Paginate through `messages().list`.
    - For each message, fetch details.
    - efficient parsing of payload (headers, mime-parts) to extract body.
    - Upsert into `Email` table (avoid duplicates if same email fetched twice).
    - Update `EmailDumpTask` status to `COMPLETED`.

## 5. API Endpoints Specification

### Auth
- `GET /api/v1/auth/login`: Returns the Google OAuth authorization URL.
- `GET /api/v1/auth/callback`: Handles the redirect from Google, exchanges code for tokens, saves `GmailConnection`.

### Dumps
- `POST /api/v1/dumps/`: Create a new dump task.
    - Body: `{ "connection_id": "...", "criteria": "recipient", "value": "bob@example.com" }`
- `GET /api/v1/dumps/`: List all dump tasks.
- `GET /api/v1/dumps/{id}`: Get status and stats of a specific task.

### Email View
- `GET /api/v1/emails/`: key endpoint for "Gmail-like view".
    - Params: `page`, `limit`, `sort_by`, `thread_id`, `search`.
- `GET /api/v1/emails/{id}`: Get full details of a single email.
- `GET /api/v1/emails/{id}/attachments`: Download attachments (if implemented).

### Export
- `GET /api/v1/export/{dump_id}`: Generates a JSON or CSV dump of all emails linked to a task.

## 6. Next Steps
1.  Initialize FastAPI project structure.
2.  Set up Google Cloud Console inputs (Client ID/Secret) - *User needs to provide this or we use placeholders*.
3.  Implement Models and Database connection.
4.  Implement Basic Auth Flow.
5.  Implement Fetch/Dump Logic.

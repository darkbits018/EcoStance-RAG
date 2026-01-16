# Frontend Implementation Plan - Custom CRM (Email Dump)

## 1. Project Overview
This frontend application will serve as the user interface for the Custom CRM, specifically focused on the Email Dump features. It will interact with the FastAPI backend to manage Gmail connections, trigger email dumps, and explore fetched emails in a Gmail-like interface.

## 2. Tech Stack
- **Build Tool**: Vite
- **Framework**: React (TypeScript)
- **Styling**: Vanilla CSS (Modular & Variables for theming)
- **Routing**: React Router DOM
- **HTTP Client**: Axios (or native Fetch)
- **Icons**: Lucide React or similar

## 3. Directory Structure
```text
c-crm-fe/
├── public/
├── src/
│   ├── assets/              # Images, global CSS
│   ├── components/
│   │   ├── common/          # Buttons, Inputs, Modals (UI Kit)
│   │   ├── layout/          # Sidebar, Header
│   │   ├── connections/     # Connection management & Auth status
│   │   ├── dumps/           # Dump task list & creation form
│   │   └── emails/          # Email list, Thread view, Message render
│   ├── contexts/            # AuthContext, ToastContext
│   ├── hooks/               # Custom hooks (useFetch, useAuth)
│   ├── pages/
│   │   ├── DashboardPage.tsx
│   │   ├── ConnectionsPage.tsx
│   │   ├── DumpsPage.tsx
│   │   ├── EmailBrowserPage.tsx
│   └── services/
│       ├── api.ts           # Axios instance
│       ├── authService.ts
│       └── emailService.ts
│   ├── App.tsx
│   └── main.tsx
├── index.html
└── package.json
```

## 4. Key Features & Modules

### 4.1. Authentication & Connections
- **Goal**: Manage Google OAuth connections.
- **UI**:
    - A "Connect Gmail" button that redirects to `http://localhost:8000/api/v1/auth/login`.
    - List of active connections (e.g., "Connected as bob@example.com").
    - Status indicators (Active/Expired).

### 4.2. Dump Management
- **Goal**: Trigger and monitor email fetch tasks.
- **UI**:
    - **Create Dump**: Form to select a connection and define criteria (e.g., "Emails from x", "Label y").
    - **Tasks List**: Table showing Status (Pending/Processing/Done), Start Time, Total Emails.
    - **Auto-refresh**: Polling to update status.

### 4.3. Email Browser (Gmail-like View)
- **Goal**: View stored emails without hitting Gmail API directly.
- **UI**:
    - **Split Layout**: List on the left (or top), Detail view on the right (or modal/page).
    - **List Item**: Sender, Subject, Snippet, Date.
    - **Detail View**: Full HTML body rendering (sanitized), Metadata (Thread ID, Labels).
    - **Search/Filter**: Search bar to query the local database via Backend API.

### 4.4. Export
- **Goal**: Download data.
- **UI**: Simple "Export to JSON/CSV" button on the Dump details or Email List page.

## 5. Development Phases

### Phase 1: Setup & Foundation
- Initialize Vite React TS project.
- Set up Vanilla CSS variables (Colors, Typography) for a premium "Glassmorphism" look.
- Create generic components (Card, Button, Input).

### Phase 2: Core Integration
- Implement API service layer.
- Build "Connections" page to handle OAuth flow (mostly checking status).
- Build "Dumps" page to trigger backend tasks.

### Phase 3: The Email Browser
- Build the Email List component.
- Build the Email Detail renderer (HTML sanitization).
- Implement Pagination.

### Phase 4: Polish
- Loading states (Skeleton screens).
- Error handling (Toasts).
- Responsive adjustments.

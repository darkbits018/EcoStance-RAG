# RBAC & Invitation System Integration Guide

## 1. Backend Changes Overview

We have refactored the backend to support a robust Role-Based Access Control (RBAC) system and a secure user invitation flow. This replaces the simple user creation logic with a full invite-accept lifecycle.

### Key Architectural Changes

*   **Invitation Logic**: Admins no longer set passwords for users. Instead, they trigger an invitation which sends a secure link via email.
*   **Token-Based Acceptance**: A specific JWT token type (`invite`) is generated for new users, valid for 48 hours.
*   **Role Management**: Users are assigned a `role_id` corresponding to defined Tenant Roles (e.g., "Admin", "Editor", "Viewer").

### API Endpoints Reference

#### a. User Management (Tenant Admin)
| Method | Endpoint | Description | Payload |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/tenant/users` | List all users in tenant | - |
| `POST` | `/api/v1/tenant/users/invite` | Invite single user | `{ "email": "...", "full_name": "...", "role_id": "..." }` |
| `POST` | `/api/v1/tenant/users/invite-bulk` | Invite multiple users | `{ "emails": ["..."], "role_id": "..." }` |
| `PUT` | `/api/v1/tenant/users/{id}` | Update user details | `{ "full_name": "...", "role_id": "...", "is_active": bool }` |
| `DELETE` | `/api/v1/tenant/users/{id}` | Remove a user | **Returns 204 No Content (Empty Body)** |

#### b. Role Management
| Method | Endpoint | Description | Payload |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/tenant/roles` | Get available roles | - |
| `POST` | `/api/v1/tenant/roles` | Create custom role | `{ "name": "...", "permissions": [...] }` |

#### c. Authentication (Public/Accept Flow)
| Method | Endpoint | Description | Payload |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/set-password` | Set password via invite | `{ "token": "...", "password": "..." }` |

---

## 2. React Frontend Implementation Guide

This section outlines the pages and dynamic components required in the React application to support these features. **Do not implement hardcoded roles; fetch them dynamically.**

### A. User Management Page (Protected)

This page should be accessible only to users with `TENANT_MANAGE_USERS` permission (typically Admins).

**1. Users List View**
*   **Action**: On mount, call `GET /api/v1/tenant/users`.
*   **Display**: Table showing Name, Email, Role (Name), Status (Active/Pending), and Joined Date.
*   **Interactions**:
    *   "Invite User" button (opens modal).
    *   "Edit" action (opens modal to change Role or Active status).
    *   "Delete" action (with confirmation).


**2. Invite User Modal (Bulk Support)**

The invite system has been upgraded to support multiple email invitations at once.

*   **Preparation**: On open, call `GET /api/v1/tenant/roles` to populate the role dropdown.
*   **Form Fields**:
    *   **Emails** (Text Area, required): Allow users to input multiple emails (e.g., comma, space, or newline separated).
    *   **Role** (Select dropdown, required): Applies to all invited users.
*   **Submission Strategy**:
    *   Parse the input string into a list of email strings.
    *   POST to `/api/v1/tenant/users/invite-bulk` with payload: `{ "emails": ["a@test.com", "b@test.com"], "role_id": "..." }`.
    *   **Response Handling**: The API returns a split result: `{ "successful": [...], "failed": [{"email": "...", "reason": "..."}] }`.
*   **UI Feedback**:
    *   Show a summary toast or alert: "Invited X users successfully."
    *   If there are failures, display them clearly (e.g., "Skipped 2 users: user@exists.com (Already exists)").
    *   Close modal if all successful, otherwise keep open to let user fix errors? (Design choice).

### B. Invitation Acceptance Page (Public)

This page handles the "First Time Login" experience where invited users set their initial password.

*   **Route Setup**: Create a new public route (e.g., `/auth/set-password` in React Router). 
    *   **CRITICAL**: This route must **NOT** be wrapped in an authentication guard. It must be accessible anonymously.
*   **Query Param Handling**: 
    *   On component mount, extract the `invite_token` from the URL: `window.location.search` or `useSearchParams()`.
    *   If no token is found, redirect to `/login`.
*   **User UI**:
    *   Fields: `New Password`, `Confirm Password`.
    *   Display a message: "Welcome to the platform! Please set a password for your new account."
*   **API Submission**:
    *   **Endpoint**: `POST /api/v1/auth/set-password`
    *   **Payload**: `{ "token": "TOKEN_FROM_URL", "password": "NEW_PASSWORD" }`
    *   *Note*: The API field name is `token`, but the URL parameter we use is `invite_token`.
*   **Post-Submission Logic**:
    *   **On Success**: Show a success state or "Success" toast. Wait 2 seconds, then redirect to the main `/login` page.
    *   **On Failure**: Show specific error (e.g., "Link expired", "Token invalid"). Provide a link back to the login page.

### C. Updates to App State / Context

**1. Login Response Handling**
*   The login response now includes `role` information.
*   Ensure your Auth Context stores this role to conditionally render the "Users" navigation item (only if they are an Admin or have permission).

**2. Navigation Menu**
*   Add **"Users"** or **"Team"** item to the main sidebar.
*   Protect this item: Hide it if the current user does not have the required permissions.

### Summary of Tasks for Frontend Developer
1.  Create `UserManagement` page with List and Invite functionalities.
2.  Create `SetPassword` page for the public route handling invite tokens.
3.  Integrate `RoleService` to fetch roles dynamically for dropdowns.
4.  Update API client to handle the new endpoints.

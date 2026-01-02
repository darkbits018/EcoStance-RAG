# Tenant User Management Endpoints

The following endpoints have been added to manage users within an organization (Tenant). 
All endpoints ensure tenant isolation by strictly filtering data using the authenticated user's `tenant_id`.

## Base URL
`/api/v1/tenant`

## Endpoints

### 1. Invite/Create User
**POST** `/users`
Creates a new user record in the tenant.
- **Permission**: `TENANT_MANAGE_USERS`
- **Body**:
  ```json
  {
    "email": "newuser@example.com",
    "full_name": "New User",
    "role_id": "optional-role-uuid"
  }
  ```

### 2. List Users
**GET** `/users`
Lists all users belonging to the current tenant.
- **Permission**: `TENANT_VIEW`
- **Response**: Array of user objects with role details.

### 3. Get User Details
**GET** `/users/{user_id}`
- **Permission**: `TENANT_VIEW`

### 4. Update User
**PUT** `/users/{user_id}`
Updates user details or role assignment.
- **Permission**: `TENANT_MANAGE_USERS`
- **Body**:
  ```json
  {
    "full_name": "Updated Name",
    "is_active": true,
    "role_id": "new-role-uuid"
  }
  ```

### 5. Remove User
**DELETE** `/users/{user_id}`
Removes a user from the tenant.
- **Permission**: `TENANT_MANAGE_USERS`
- **Constraint**: Users cannot delete themselves.

## Security Controls
1.  **Tenant Isolation**: All database queries include `tenant_id == current_user.tenant_id`.
2.  **RBAC**: Every endpoint enforces specific permissions via `RBACService`.
3.  **Role Validation**: When assigning roles, the system verifies the Role ID actually belongs to the same tenant.

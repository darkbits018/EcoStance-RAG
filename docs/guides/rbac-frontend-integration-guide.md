# Better RBAC Frontend Integration Guide

## Overview

This document provides comprehensive guidance for frontend developers to integrate with the new Better RBAC (Role-Based Access Control) system. The system implements a two-tier role architecture with flexible permission management, replacing the previous static role system.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Authentication Integration](#authentication-integration)
3. [API Endpoints Reference](#api-endpoints-reference)
4. [User Interface Components](#user-interface-components)
5. [Permission Management](#permission-management)
6. [Role Management](#role-management)
7. [System Administration](#system-administration)
8. [User Experience Guidelines](#user-experience-guidelines)
9. [Error Handling](#error-handling)
10. [Security Considerations](#security-considerations)

---

## System Architecture

### Two-Tier Role System

The new RBAC system operates on two distinct levels:

**System Roles (Fixed)**
- **Super Admin**: Complete system access across all tenants
- **Tenant Admin**: Full administrative access within their organization

**Tenant Roles (Dynamic)**
- Custom roles created by tenant administrators
- Flexible permission combinations
- Organization-specific naming and descriptions

### Permission Categories

Permissions are organized into six main categories:

1. **Knowledge Base** (kb:*): Content management and queries
2. **Database** (db:*): Database connections and operations
3. **File Management** (file:*): File upload, download, and management
4. **Tenant Management** (tenant:*): Organization settings and user management
5. **Gmail Integration** (gmail:*): Email system configuration and operations
6. **System Administration** (admin:*): System-wide administrative functions

---

## Authentication Integration

### JWT Token Requirements

The frontend must include JWT tokens in API requests containing:
- **user_id**: Unique identifier for the authenticated user
- **tenant_id**: Organization identifier for the user's context

### Header Format

All API requests must include the Authorization header with a valid JWT token. The backend will extract user and tenant information from this token.

### Session Management

Implement proper session management to handle:
- Token expiration and refresh
- Role changes during active sessions
- Permission updates in real-time

---

## API Endpoints Reference

### Tenant Role Management

**Base Path**: `/api/v1/tenant/roles`

#### List Roles
- **Method**: GET
- **Endpoint**: `/roles`
- **Purpose**: Retrieve all active roles in the current tenant
- **Required Permission**: TENANT_VIEW
- **Response**: List of roles with metadata and permission counts

#### Create Role
- **Method**: POST
- **Endpoint**: `/roles`
- **Purpose**: Create a new custom role
- **Required Permission**: TENANT_MANAGE_USERS
- **Validation**: Role name must be unique within tenant

#### Update Role
- **Method**: PUT
- **Endpoint**: `/roles/{role_id}`
- **Purpose**: Modify existing role properties
- **Required Permission**: TENANT_MANAGE_USERS
- **Validation**: Cannot assign permissions the user doesn't have

#### Delete Role
- **Method**: DELETE
- **Endpoint**: `/roles/{role_id}`
- **Purpose**: Remove a role (users lose this role)
- **Required Permission**: TENANT_MANAGE_USERS
- **Warning**: Destructive action requiring confirmation

#### Role Users
- **Method**: GET
- **Endpoint**: `/roles/{role_id}/users`
- **Purpose**: List all users assigned to a specific role
- **Required Permission**: TENANT_VIEW

#### Assign Role
- **Method**: POST
- **Endpoint**: `/users/{user_id}/assign-role`
- **Purpose**: Assign a role to a user
- **Required Permission**: TENANT_MANAGE_USERS

#### Remove Role
- **Method**: DELETE
- **Endpoint**: `/users/{user_id}/remove-role`
- **Purpose**: Remove role assignment from a user
- **Required Permission**: TENANT_MANAGE_USERS

### Permission Management

**Base Path**: `/api/v1/tenant/permissions`

#### List Permissions
- **Method**: GET
- **Endpoint**: `/permissions`
- **Purpose**: Get all available permissions for role assignment
- **Required Permission**: TENANT_VIEW
- **Filter**: Only shows permissions the user can assign

#### Permission Categories
- **Method**: GET
- **Endpoint**: `/permissions/categories`
- **Purpose**: Get permissions grouped by functional category
- **Required Permission**: TENANT_VIEW
- **Use Case**: Organize permission selection in UI

#### My Permissions
- **Method**: GET
- **Endpoint**: `/permissions/my-permissions`
- **Purpose**: Get current user's permissions and role information
- **Use Case**: UI state management and feature visibility

### System Administration

**Base Path**: `/api/v1/admin`

#### List Tenants
- **Method**: GET
- **Endpoint**: `/tenants`
- **Purpose**: View all organizations in the system
- **Required Permission**: ADMIN_VIEW_ALL (Super Admin only)

#### Tenant Users
- **Method**: GET
- **Endpoint**: `/tenants/{tenant_id}/users`
- **Purpose**: View all users within a specific tenant
- **Required Permission**: ADMIN_MANAGE_USERS (Super Admin only)

#### Promote User
- **Method**: POST
- **Endpoint**: `/tenants/{tenant_id}/promote-admin`
- **Purpose**: Assign system roles to users
- **Required Permission**: ADMIN_MANAGE_USERS (Super Admin only)

#### System Roles
- **Method**: GET
- **Endpoint**: `/system/roles`
- **Purpose**: View all system role assignments
- **Required Permission**: ADMIN_VIEW_ALL (Super Admin only)

#### System Metrics
- **Method**: GET
- **Endpoint**: `/metrics`
- **Purpose**: Get system-wide RBAC statistics
- **Required Permission**: ADMIN_VIEW_METRICS (Super Admin only)

---

## User Interface Components

### Role Management Dashboard

**Primary Features**:
- Role list with search and filtering
- Permission count and active user indicators
- Quick actions for edit, delete, and view users
- Create new role button with permission validation

**Layout Considerations**:
- Tabular view for role listing
- Card-based layout for role details
- Modal dialogs for create/edit operations
- Confirmation dialogs for destructive actions

### Permission Selection Interface

**Design Requirements**:
- Categorized permission display
- Search and filter capabilities
- Bulk selection options
- Clear permission descriptions
- Visual indicators for assigned permissions

**User Experience**:
- Group permissions by category for easier navigation
- Provide tooltips explaining each permission
- Show permission dependencies if applicable
- Highlight permissions the user cannot assign

### User Role Assignment

**Interface Elements**:
- User search and selection
- Current role display
- Available roles dropdown
- Role change confirmation
- Bulk assignment capabilities

**Workflow Considerations**:
- Show user's current permissions before and after role change
- Provide role comparison functionality
- Include role assignment history
- Support role removal with clear warnings

### System Administration Panel

**Super Admin Features**:
- Tenant overview with user statistics
- System role assignment interface
- Cross-tenant user management
- System-wide metrics and reporting

**Security Measures**:
- Clear indication of super admin context
- Confirmation for system-level changes
- Audit trail display
- Emergency access controls

---

## Permission Management

### Permission Display

**Categorization Strategy**:
- Group by functional area (KB, DB, File, etc.)
- Use consistent iconography for each category
- Provide expandable sections for detailed permissions
- Show permission hierarchy where applicable

**Permission Descriptions**:
- Use clear, non-technical language
- Explain the scope and impact of each permission
- Provide examples of what the permission allows
- Include security implications for sensitive permissions

### Permission Validation

**Frontend Validation**:
- Check user's permissions before showing assignment options
- Disable permissions the user cannot assign
- Provide clear feedback for permission conflicts
- Validate role combinations for logical consistency

**Real-time Updates**:
- Refresh permission lists when user roles change
- Update UI state based on current permissions
- Handle permission revocation gracefully
- Maintain consistent state across browser tabs

---

## Role Management

### Role Creation Workflow

**Step-by-Step Process**:
1. Role name and description input
2. Permission selection with category grouping
3. Permission validation and conflict checking
4. Role preview with permission summary
5. Confirmation and creation

**Validation Requirements**:
- Unique role names within tenant
- At least one permission must be selected
- Cannot assign permissions user doesn't have
- Role description should be meaningful

### Role Editing Interface

**Edit Capabilities**:
- Modify role name and description
- Add or remove permissions
- Activate or deactivate roles
- View role usage statistics

**Change Impact Analysis**:
- Show affected users before making changes
- Highlight permission additions and removals
- Provide rollback options for recent changes
- Display change history and audit trail

### Role Templates

**Predefined Roles**:
- Viewer: Basic read-only access
- User: Standard operational permissions
- Manager: Extended management capabilities
- Gmail Administrator: Email system control

**Template Customization**:
- Allow modification of template roles
- Provide role duplication functionality
- Support role import/export between tenants
- Enable role sharing across organizations

---

## System Administration

### Tenant Management Interface

**Tenant Overview**:
- Organization information and statistics
- User count and role distribution
- Active role summary
- Recent activity indicators

**Cross-Tenant Operations**:
- User search across all tenants
- System role assignment interface
- Bulk operations for multiple tenants
- Global policy enforcement tools

### System Metrics Dashboard

**Key Metrics Display**:
- Total tenants and users
- Role distribution statistics
- Permission usage analytics
- Migration status indicators

**Reporting Features**:
- Exportable reports in multiple formats
- Scheduled report generation
- Custom metric filtering
- Historical trend analysis

### Audit and Compliance

**Audit Trail Interface**:
- Role change history
- Permission modification logs
- User assignment tracking
- System access records

**Compliance Reporting**:
- Role certification workflows
- Access review processes
- Compliance violation alerts
- Regulatory reporting tools

---

## User Experience Guidelines

### Navigation and Information Architecture

**Menu Structure**:
- Separate sections for role management and user management
- Clear distinction between tenant and system administration
- Contextual navigation based on user permissions
- Breadcrumb navigation for complex workflows

**Information Hierarchy**:
- Prioritize most common tasks
- Group related functions together
- Provide shortcuts for frequent operations
- Maintain consistent layout patterns

### Visual Design Principles

**Role and Permission Visualization**:
- Use consistent color coding for permission categories
- Implement clear iconography for different role types
- Provide visual indicators for active/inactive states
- Use progressive disclosure for complex information

**Status and Feedback**:
- Clear success and error messaging
- Loading states for API operations
- Progress indicators for multi-step processes
- Contextual help and guidance

### Accessibility Considerations

**Inclusive Design**:
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Scalable text and interface elements

**Usability Features**:
- Tooltips and contextual help
- Undo functionality where appropriate
- Confirmation dialogs for destructive actions
- Clear error messages with resolution guidance

---

## Error Handling

### API Error Responses

**Common Error Scenarios**:
- Insufficient permissions (403 Forbidden)
- Resource not found (404 Not Found)
- Validation failures (400 Bad Request)
- Server errors (500 Internal Server Error)

**Error Message Guidelines**:
- Provide clear, actionable error messages
- Include specific details about what went wrong
- Suggest resolution steps where possible
- Maintain consistent error message formatting

### User-Friendly Error Handling

**Permission Errors**:
- Explain why the action is not allowed
- Suggest alternative actions or contacts
- Provide links to request additional permissions
- Show current permission level for context

**Validation Errors**:
- Highlight specific form fields with issues
- Provide inline validation feedback
- Explain validation rules clearly
- Offer suggestions for valid inputs

### Recovery Mechanisms

**Graceful Degradation**:
- Disable unavailable features rather than hiding them
- Provide read-only views when edit permissions are missing
- Maintain partial functionality during system issues
- Cache critical data for offline scenarios

---

## Security Considerations

### Frontend Security Measures

**Token Management**:
- Secure token storage (avoid localStorage for sensitive tokens)
- Automatic token refresh mechanisms
- Proper token cleanup on logout
- Session timeout handling

**Permission Enforcement**:
- Never rely solely on frontend permission checks
- Hide UI elements based on permissions but validate on backend
- Implement proper route guards for protected pages
- Validate user actions against current permissions

### Data Protection

**Sensitive Information Handling**:
- Minimize exposure of user data in UI
- Implement proper data masking where needed
- Secure transmission of role and permission data
- Audit logging for sensitive operations

**Cross-Tenant Security**:
- Ensure proper tenant isolation in UI
- Validate tenant context for all operations
- Prevent cross-tenant data leakage
- Implement proper access controls for multi-tenant users

### Audit and Monitoring

**User Activity Tracking**:
- Log significant role and permission changes
- Track user access patterns
- Monitor for suspicious activities
- Provide audit trail visibility to administrators

**Security Incident Response**:
- Implement emergency access controls
- Provide mechanisms for immediate permission revocation
- Support security incident investigation
- Enable rapid response to security threats

---

## Implementation Checklist

### Phase 1: Basic Integration
- [ ] Implement JWT token handling
- [ ] Create basic role listing interface
- [ ] Add permission display components
- [ ] Implement user role assignment

### Phase 2: Advanced Features
- [ ] Build role creation and editing workflows
- [ ] Add permission categorization and search
- [ ] Implement system administration interface
- [ ] Create audit and reporting features

### Phase 3: User Experience Enhancement
- [ ] Add advanced filtering and search capabilities
- [ ] Implement bulk operations
- [ ] Create role templates and presets
- [ ] Add comprehensive help and documentation

### Phase 4: Security and Compliance
- [ ] Implement comprehensive audit logging
- [ ] Add compliance reporting features
- [ ] Create security monitoring dashboards
- [ ] Implement emergency access controls

---

## Conclusion

The Better RBAC system provides a flexible, secure, and scalable approach to access control management. This frontend integration guide provides the foundation for building a comprehensive user interface that leverages all the system's capabilities while maintaining security and usability standards.

The implementation should prioritize user experience while ensuring that security measures are never compromised. Regular testing and validation against the API endpoints will ensure a robust and reliable integration.

For technical implementation details and API specifications, refer to the Better RBAC technical documentation and API reference materials.
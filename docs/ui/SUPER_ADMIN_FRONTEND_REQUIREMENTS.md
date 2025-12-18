# Super Admin Frontend Requirements

**Platform:** Multi-Tenant RAG & AI Agent Platform  
**User Role:** Super Admin (Platform Administrator)  
**Purpose:** Manage all tenants, monitor system health, and configure platform-wide settings

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication & Access](#authentication--access)
3. [Dashboard Pages](#dashboard-pages)
4. [Feature Requirements](#feature-requirements)
5. [UI/UX Guidelines](#uiux-guidelines)
6. [API Endpoints Reference](#api-endpoints-reference)

---

## Overview

The Super Admin frontend is a separate administrative interface for platform operators to manage the entire multi-tenant system. It provides cross-tenant visibility and control over all aspects of the platform.

**Key Characteristics:**
- Separate from tenant user interface
- Requires `super_admin` role
- Cross-tenant data access
- System-wide monitoring and control
- Advanced configuration options

---

## Authentication & Access

### Login Page

**URL:** `/admin/login`

**Features:**
- Email/password authentication
- "Remember me" option
- Forgot password link
- Branding: Platform logo (not tenant-specific)
- Security: Rate limiting, CAPTCHA after failed attempts

**API Endpoint:**
```
POST /api/v1/auth/login
Body: { email, password }
Response: { access_token, refresh_token, user: { role: "super_admin" } }
```

**Access Control:**
- Check if user has `super_admin` role
- Redirect non-super-admins to tenant login
- Session timeout: 8 hours (configurable)

---

## Dashboard Pages

### 1. Main Dashboard

**URL:** `/admin/dashboard`

**Purpose:** High-level overview of platform health and activity

**Sections:**

#### A. Key Metrics Cards (Top Row)
- **Total Tenants**
  - Count of active tenants
  - Growth trend (vs last month)
  - Icon: Building/Organization
  
- **Total Users**
  - Count across all tenants
  - Active users (last 30 days)
  - Icon: Users
  
- **Total Queries Today**
  - RAG queries + Agent queries
  - Comparison to yesterday
  - Icon: Search/Query
  
- **System Health**
  - Status: Healthy/Warning/Critical
  - Uptime percentage
  - Icon: Heart/Pulse

#### B. Platform Activity Chart
- Line chart showing queries over time (last 30 days)
- Separate lines for RAG queries vs Agent queries
- Filterable by date range

#### C. Tenant Growth Chart
- Bar chart showing new tenant registrations per month
- Last 12 months
- Hover to see exact numbers

#### D. Recent Activity Feed
- Last 20 system events
- Types: Tenant created, Tenant suspended, Quota exceeded, System errors
- Each item shows: Timestamp, Event type, Tenant name, Details
- Real-time updates (WebSocket or polling)

#### E. Quick Actions
- Create New Tenant (button)
- View All Tenants (button)
- System Settings (button)
- Run Cleanup Tasks (button)

**API Endpoints:**
```
GET /api/v1/admin/dashboard/summary
Response: {
  total_tenants, total_users, total_queries_today,
  system_health, activity_chart_data, tenant_growth_data,
  recent_events
}
```

---

### 2. Tenant Management

**URL:** `/admin/tenants`

**Purpose:** View, search, and manage all tenant organizations

#### A. Tenant List Table

**Features:**
- Searchable (by name, email, ID)
- Sortable columns
- Filterable (by status, tier, date created)
- Pagination (50 per page)
- Bulk actions (suspend, change tier)

**Columns:**
1. **Tenant Name** - Clickable to view details
2. **Company** - Organization name
3. **Status** - Badge (Active/Suspended/Inactive)
4. **Tier** - Badge (Free/Pro/Enterprise)
5. **Users** - Count of users in tenant
6. **KBs** - Count of knowledge bases
7. **Storage** - Used storage (GB)
8. **Queries (30d)** - Query count last 30 days
9. **Created** - Date created
10. **Actions** - Dropdown menu

**Actions Menu:**
- View Details
- Edit Tenant
- Change Tier
- Suspend/Reactivate
- View Activity
- Export Data
- Delete Tenant (with confirmation)

**Filters:**
- Status: All, Active, Suspended, Inactive
- Tier: All, Free, Pro, Enterprise
- Date Range: Last 7 days, 30 days, 90 days, All time
- Sort by: Name, Created date, Query count, Storage

**Search:**
- Real-time search as you type
- Search by: Tenant name, company name, email, tenant ID

**API Endpoints:**
```
GET /api/v1/admin/tenants/search?q={query}&status={status}&tier={tier}
GET /api/v1/tenants (list all)
PATCH /api/v1/admin/tenants/{id}/tier
POST /api/v1/admin/tenants/{id}/suspend
POST /api/v1/admin/tenants/{id}/reactivate
DELETE /api/v1/admin/tenants/{id}
```

#### B. Create Tenant Modal

**Trigger:** "Create New Tenant" button

**Form Fields:**
- Tenant Name* (required)
- Company Name*
- Admin Email* (will receive login credentials)
- Admin Password* (or auto-generate)
- Tier* (dropdown: Free/Pro/Enterprise)
- Initial Quota Settings (optional, defaults by tier)
  - Max queries per day
  - Max storage (GB)
  - Max knowledge bases
- Notes (optional, internal use)

**Actions:**
- Create & Send Email (creates tenant + emails admin)
- Create Only (creates tenant, no email)
- Cancel

**API Endpoint:**
```
POST /api/v1/tenants/register
Body: { name, company, email, password, tier, quotas }
```

---

### 3. Tenant Details Page

**URL:** `/admin/tenants/{tenant_id}`

**Purpose:** Detailed view and management of a single tenant

#### A. Tenant Overview (Top Section)

**Info Cards:**
- Tenant Name & Company
- Status badge with toggle (Active/Suspended)
- Tier badge with edit button
- Created date
- Last activity timestamp
- Admin contact email

**Quick Stats:**
- Total Users
- Total Knowledge Bases
- Total Documents
- Storage Used / Limit
- Queries (30d) / Limit

#### B. Tabs

**Tab 1: Activity**
- Timeline of tenant activities
- Filters: All, Logins, Uploads, Queries, Errors
- Date range selector
- Export to CSV

**Tab 2: Users**
- List of all users in tenant
- Columns: Name, Email, Role, Status, Last Login
- Actions: View, Suspend, Delete
- Add User button

**Tab 3: Knowledge Bases**
- List of all KBs
- Columns: Name, Documents, Vectors, Storage, Created
- Actions: View, Delete
- View documents in KB

**Tab 4: Usage & Metrics**
- Charts:
  - Queries over time (last 30 days)
  - Storage usage over time
  - API calls by endpoint
- Tables:
  - Top queried KBs
  - Most active users
  - Error summary

**Tab 5: Quotas & Limits**
- Current quota settings (editable)
- Usage vs limits (progress bars)
- Quota history (changes over time)
- Edit Quotas button

**Tab 6: Settings**
- Tenant-specific settings
- Public chat enabled/disabled
- Public agent enabled/disabled
- Custom branding settings
- Danger zone: Delete tenant

**API Endpoints:**
```
GET /api/v1/tenants/{id}
GET /api/v1/admin/tenants/{id}/activity
GET /api/v1/admin/tenants/{id}/storage
PUT /api/v1/tenants/{id}
PUT /api/v1/admin/quotas/{tenant_id}
```

---

### 4. System Health & Monitoring

**URL:** `/admin/system`

**Purpose:** Monitor platform infrastructure and performance

#### A. System Status Dashboard

**Service Status Cards:**
- **API Server**
  - Status: Online/Offline
  - Uptime: 99.9%
  - Response time: 45ms avg
  - Requests/min: 1,234
  
- **Database (PostgreSQL)**
  - Status: Online/Offline
  - Connections: 45/100
  - Query time: 12ms avg
  - Storage: 45GB / 100GB
  
- **Vector Store (Qdrant)**
  - Status: Online/Offline
  - Collections: 156
  - Vectors: 2.3M
  - Memory: 8GB / 16GB
  
- **Background Jobs**
  - Status: Running/Stopped
  - Active jobs: 3
  - Failed jobs (24h): 2
  - Next scheduled: 2 hours

#### B. Performance Metrics

**Charts:**
- API Response Times (last 24 hours)
- Error Rate (last 24 hours)
- Database Query Performance
- Memory Usage
- CPU Usage

**Alerts:**
- List of active alerts
- Types: High error rate, Slow queries, Low disk space
- Severity: Critical, Warning, Info
- Acknowledge/Dismiss buttons

#### C. Recent Errors

**Error Log Table:**
- Timestamp
- Severity (Critical/Error/Warning)
- Component (API/Database/Qdrant/Jobs)
- Error message
- Tenant ID (if applicable)
- Stack trace (expandable)
- Actions: View details, Mark as resolved

**Filters:**
- Severity
- Component
- Date range
- Tenant

**API Endpoints:**
```
GET /api/v1/admin/health/system
Response: {
  api_status, database_status, qdrant_status,
  background_jobs_status, performance_metrics,
  active_alerts, recent_errors
}
```

---

### 5. Usage Analytics

**URL:** `/admin/analytics`

**Purpose:** Platform-wide usage analytics and insights

#### A. Overview Metrics (Top)

**Time Period Selector:** Last 7 days, 30 days, 90 days, Custom range

**Metric Cards:**
- Total Queries (period)
- Total Documents Uploaded
- Total Storage Used
- Active Tenants (queried in period)
- Average Queries per Tenant
- Average Response Time

#### B. Charts & Visualizations

**Query Analytics:**
- Queries over time (line chart)
- Queries by tenant (bar chart, top 10)
- Queries by endpoint (pie chart: RAG vs Agent vs Public)
- Peak usage hours (heatmap)

**Storage Analytics:**
- Storage growth over time (area chart)
- Storage by tenant (bar chart, top 10)
- Storage by file type (pie chart)

**User Analytics:**
- Active users over time
- New user registrations
- User activity by tenant

**Performance Analytics:**
- Average response time trend
- Error rate trend
- Success rate by endpoint

#### C. Export Options

- Export to CSV
- Export to PDF report
- Schedule automated reports (email)

**API Endpoints:**
```
GET /api/v1/usage/summary?start_date={date}&end_date={date}
GET /api/v1/usage/by-endpoint
GET /api/v1/metrics/performance
```

---

### 6. Quota Management

**URL:** `/admin/quotas`

**Purpose:** Manage resource quotas and limits across all tenants

#### A. Quota Templates

**Default Tier Settings:**

**Free Tier Card:**
- Max queries per day: 100
- Max queries per month: 3,000
- Max documents: 100
- Max storage: 1 GB
- Max knowledge bases: 2
- Max concurrent queries: 2
- Edit Template button

**Pro Tier Card:**
- Max queries per day: 1,000
- Max queries per month: 30,000
- Max documents: 1,000
- Max storage: 10 GB
- Max knowledge bases: 10
- Max concurrent queries: 5
- Edit Template button

**Enterprise Tier Card:**
- Max queries per day: 10,000
- Max queries per month: 300,000
- Max documents: Unlimited
- Max storage: 100 GB
- Max knowledge bases: Unlimited
- Max concurrent queries: 20
- Edit Template button

**Actions:**
- Edit tier defaults
- Apply to all tenants in tier
- Create custom tier

#### B. Tenant Quota Overrides

**Table:**
- List of tenants with custom quotas (different from tier defaults)
- Columns: Tenant, Tier, Custom Quotas, Applied Date
- Actions: Edit, Reset to default

**Search & Filter:**
- Search by tenant name
- Filter by tier
- Filter by: Has overrides, Exceeding limits

#### C. Quota Alerts

**Alert Rules:**
- Notify when tenant reaches 80% of quota
- Notify when tenant exceeds quota
- Notify when multiple tenants exceed quotas
- Email/Slack notification settings

**Recent Quota Events:**
- Tenant exceeded daily query limit
- Tenant reached storage limit
- Quota increased for tenant
- Timestamp, Tenant, Event type

**API Endpoints:**
```
GET /api/v1/admin/quotas/templates
PUT /api/v1/admin/quotas/templates/{tier}
GET /api/v1/admin/quotas/overrides
PUT /api/v1/admin/quotas/{tenant_id}
```

---

### 7. Cleanup & Maintenance

**URL:** `/admin/maintenance`

**Purpose:** Run cleanup tasks and maintain system health

#### A. Cleanup Tasks

**Available Tasks (Cards):**

**1. Cleanup Old Sessions**
- Description: Remove expired user sessions
- Last run: 2 hours ago
- Items to clean: ~150 sessions
- Max age: 24 hours (configurable)
- Button: Run Now

**2. Cleanup Temp Files**
- Description: Remove temporary uploaded files
- Last run: 1 day ago
- Items to clean: ~45 files (2.3 GB)
- Max age: 7 days (configurable)
- Button: Run Now

**3. Archive Audit Logs**
- Description: Archive old audit logs to cold storage
- Last run: 30 days ago
- Items to archive: ~50,000 logs
- Max age: 90 days (configurable)
- Button: Run Now

**4. Optimize Database**
- Description: Run VACUUM and ANALYZE on PostgreSQL
- Last run: 7 days ago
- Estimated time: 10-15 minutes
- Button: Run Now

**5. Cleanup Orphaned Vectors**
- Description: Remove vectors without associated documents
- Last run: Never
- Items to clean: Unknown (scan required)
- Button: Scan & Clean

#### B. Scheduled Tasks

**Cron Jobs Table:**
- Task name
- Schedule (cron expression)
- Last run
- Next run
- Status (Enabled/Disabled)
- Actions: Edit, Disable, Run now

**Default Schedule:**
- Daily cleanup: Every day at 2 AM
- Weekly optimization: Every Sunday at 3 AM
- Monthly archival: 1st of month at 4 AM

#### C. Task History

**Recent Runs:**
- Timestamp
- Task name
- Status (Success/Failed)
- Duration
- Items processed
- Logs (expandable)

**API Endpoints:**
```
POST /api/v1/admin/cleanup/sessions
POST /api/v1/admin/cleanup/temp-files
POST /api/v1/admin/cleanup/audit-logs
POST /api/v1/admin/cleanup/all
```

---

### 8. Platform Settings

**URL:** `/admin/settings`

**Purpose:** Configure platform-wide settings

#### A. General Settings

**Platform Information:**
- Platform Name (editable)
- Platform Logo (upload)
- Support Email
- Terms of Service URL
- Privacy Policy URL

**Registration Settings:**
- Allow self-service registration (toggle)
- Require email verification (toggle)
- Default tier for new tenants (dropdown)
- Auto-approve registrations (toggle)

#### B. Security Settings

**Authentication:**
- JWT token expiration (minutes)
- Refresh token expiration (days)
- Max login attempts before lockout
- Lockout duration (minutes)
- Require strong passwords (toggle)
- Password minimum length

**Rate Limiting:**
- Requests per minute (global)
- Requests per minute (per tenant)
- Requests per minute (per IP)

**CORS Settings:**
- Allowed origins (list)
- Allow credentials (toggle)

#### C. Email Settings

**SMTP Configuration:**
- SMTP host
- SMTP port
- SMTP username
- SMTP password (masked)
- From email address
- From name
- Test Email button

**Email Templates:**
- Welcome email
- Password reset email
- Quota exceeded email
- Edit templates

#### D. Integration Settings

**Qdrant Configuration:**
- Qdrant URL
- API Key (masked)
- Test Connection button

**Google Gemini:**
- API Key (masked)
- Model name
- Temperature
- Test API button

**Monitoring:**
- Enable error tracking (toggle)
- Error tracking service (dropdown: Sentry, etc.)
- API key

#### E. Feature Flags

**Global Features:**
- Enable public chat (toggle)
- Enable public agent (toggle)
- Enable AI agent (toggle)
- Enable database connections (toggle)
- Enable file uploads (toggle)

**Experimental Features:**
- Enable beta features (toggle)
- List of beta features with toggles

**API Endpoints:**
```
GET /api/v1/admin/settings
PUT /api/v1/admin/settings
POST /api/v1/admin/settings/test-email
POST /api/v1/admin/settings/test-qdrant
```

---

### 9. Audit Logs

**URL:** `/admin/audit-logs`

**Purpose:** View all system audit logs for compliance and security

#### A. Audit Log Table

**Columns:**
1. Timestamp
2. Tenant (name or "System")
3. User (email or "System")
4. Action (e.g., "tenant.created", "user.login", "kb.deleted")
5. Resource Type (tenant, user, kb, document)
6. Resource ID
7. Status (Success/Failed)
8. IP Address
9. Details (expandable JSON)

**Features:**
- Real-time updates
- Pagination (100 per page)
- Export to CSV
- Advanced search

#### B. Filters

**Filter Panel:**
- Date range (from/to)
- Tenant (dropdown, searchable)
- User (dropdown, searchable)
- Action type (dropdown, multi-select)
- Resource type (dropdown, multi-select)
- Status (Success/Failed/All)
- IP address (text input)

**Quick Filters:**
- Last hour
- Last 24 hours
- Last 7 days
- Last 30 days

#### C. Audit Log Details Modal

**When clicking on a log entry:**
- Full timestamp
- Tenant details
- User details
- Action description
- Resource details
- Request details (method, endpoint, body)
- Response details (status code, body)
- IP address and user agent
- Related logs (same session)

**API Endpoints:**
```
GET /api/v1/admin/audit-logs?start_date={date}&end_date={date}&tenant_id={id}&action={action}
GET /api/v1/admin/audit-logs/{log_id}
```

---

### 10. User Management (Super Admins)

**URL:** `/admin/super-admins`

**Purpose:** Manage super admin users

#### A. Super Admin List

**Table:**
- Name
- Email
- Status (Active/Inactive)
- Last Login
- Created Date
- Actions (Edit, Deactivate, Delete)

**Features:**
- Add New Super Admin button
- Search by name/email
- Filter by status

#### B. Add/Edit Super Admin Modal

**Form:**
- Full Name*
- Email*
- Password* (only for new)
- Status (Active/Inactive)
- Permissions (checkboxes):
  - Manage tenants
  - Manage users
  - View analytics
  - Manage quotas
  - System settings
  - Audit logs

**Actions:**
- Save
- Cancel

**API Endpoints:**
```
GET /api/v1/admin/users?role=super_admin
POST /api/v1/admin/users
PUT /api/v1/admin/users/{id}
DELETE /api/v1/admin/users/{id}
```

---

## Feature Requirements

### 1. Real-Time Updates

**Requirements:**
- Dashboard metrics update every 30 seconds
- Activity feed updates in real-time (WebSocket or polling)
- System health status updates every 10 seconds
- Notifications for critical events

**Implementation:**
- Use WebSocket for real-time updates
- Fallback to polling if WebSocket unavailable
- Show "Live" indicator when connected

### 2. Search & Filtering

**Requirements:**
- All tables must be searchable
- Search should be instant (client-side for small datasets, server-side for large)
- Filters should be combinable
- Save filter presets
- Clear all filters button

### 3. Data Export

**Requirements:**
- Export tables to CSV
- Export charts as PNG/SVG
- Generate PDF reports
- Schedule automated reports (email)

**Export Options:**
- Current view (filtered data)
- All data
- Custom date range

### 4. Notifications

**Requirements:**
- In-app notifications (bell icon)
- Email notifications (configurable)
- Slack notifications (optional)

**Notification Types:**
- Tenant exceeded quota
- System error occurred
- New tenant registered
- Cleanup task completed
- Security alert

### 5. Responsive Design

**Requirements:**
- Desktop-first design (primary use case)
- Tablet support (limited functionality)
- Mobile: Login only, redirect to desktop for full features

**Breakpoints:**
- Desktop: 1920px, 1440px, 1280px
- Tablet: 1024px, 768px
- Mobile: 640px, 375px

### 6. Performance

**Requirements:**
- Initial page load: < 2 seconds
- Table rendering: < 500ms for 1000 rows
- Chart rendering: < 1 second
- Search results: < 200ms
- API calls: < 500ms average

**Optimization:**
- Lazy loading for tables
- Virtual scrolling for large lists
- Debounced search
- Cached API responses (5 minutes)
- Optimistic UI updates

### 7. Security

**Requirements:**
- All API calls must include JWT token
- Token refresh before expiration
- Logout on token expiration
- CSRF protection
- XSS protection
- Input validation
- Audit all actions

### 8. Accessibility

**Requirements:**
- WCAG 2.1 Level AA compliance
- Keyboard navigation
- Screen reader support
- High contrast mode
- Focus indicators
- Alt text for images
- ARIA labels

---

## UI/UX Guidelines

### Design System

**Colors:**
- Primary: #0066CC (Blue)
- Secondary: #6B7280 (Gray)
- Success: #10B981 (Green)
- Warning: #F59E0B (Orange)
- Error: #EF4444 (Red)
- Background: #F9FAFB (Light Gray)
- Surface: #FFFFFF (White)
- Text Primary: #111827 (Dark Gray)
- Text Secondary: #6B7280 (Gray)

**Typography:**
- Font Family: Inter, system-ui, sans-serif
- Headings: 600 weight
- Body: 400 weight
- Code: Fira Code, monospace

**Spacing:**
- Base unit: 4px
- Scale: 4, 8, 12, 16, 24, 32, 48, 64

**Components:**
- Use consistent component library (Material-UI, Ant Design, or Chakra UI)
- Consistent button styles
- Consistent form inputs
- Consistent modals/dialogs
- Consistent tables

### Layout

**Sidebar Navigation:**
- Fixed left sidebar (240px width)
- Collapsible on smaller screens
- Active page highlighted
- Icons + labels
- Sections:
  - Dashboard
  - Tenants
  - Analytics
  - Quotas
  - System Health
  - Maintenance
  - Settings
  - Audit Logs
  - Super Admins

**Top Bar:**
- Platform logo (left)
- Search bar (center)
- Notifications icon (right)
- User menu (right)
  - Profile
  - Settings
  - Logout

**Content Area:**
- Page title (H1)
- Breadcrumbs
- Action buttons (top right)
- Main content
- Footer (optional)

### Interactions

**Loading States:**
- Skeleton screens for initial load
- Spinners for actions
- Progress bars for uploads
- Disable buttons during processing

**Empty States:**
- Friendly illustrations
- Clear message
- Call-to-action button
- Help text

**Error States:**
- Clear error message
- Suggested actions
- Retry button
- Contact support link

**Success States:**
- Toast notifications
- Success icons
- Confirmation messages
- Auto-dismiss after 5 seconds

---

## API Endpoints Reference

### Authentication
```
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET /api/v1/auth/me
```

### Dashboard
```
GET /api/v1/admin/dashboard/summary
```

### Tenant Management
```
GET /api/v1/tenants
GET /api/v1/tenants/{id}
POST /api/v1/tenants/register
PUT /api/v1/tenants/{id}
DELETE /api/v1/admin/tenants/{id}
GET /api/v1/admin/tenants/search
PATCH /api/v1/admin/tenants/{id}/tier
POST /api/v1/admin/tenants/{id}/suspend
POST /api/v1/admin/tenants/{id}/reactivate
GET /api/v1/admin/tenants/{id}/activity
GET /api/v1/admin/tenants/{id}/storage
POST /api/v1/admin/tenants/{id}/export
```

### System Health
```
GET /api/v1/admin/health/system
```

### Analytics
```
GET /api/v1/usage/summary
GET /api/v1/usage/history
GET /api/v1/usage/by-endpoint
GET /api/v1/metrics/dashboard
GET /api/v1/metrics/performance
```

### Quota Management
```
GET /api/v1/quotas/status
PUT /api/v1/admin/quotas/{tenant_id}
```

### Maintenance
```
POST /api/v1/admin/cleanup/sessions
POST /api/v1/admin/cleanup/temp-files
POST /api/v1/admin/cleanup/audit-logs
POST /api/v1/admin/cleanup/all
```

### Settings
```
GET /api/v1/admin/settings
PUT /api/v1/admin/settings
```

### Audit Logs
```
GET /api/v1/admin/audit-logs
GET /api/v1/admin/audit-logs/{id}
```

---

## Implementation Priority

### Phase 1: Core Functionality (MVP)
1. Authentication & Login
2. Main Dashboard
3. Tenant List & Search
4. Tenant Details Page
5. Basic System Health

### Phase 2: Management Features
6. Create/Edit Tenant
7. Quota Management
8. User Management
9. Suspend/Reactivate Tenants

### Phase 3: Monitoring & Analytics
10. Usage Analytics
11. System Health Details
12. Audit Logs
13. Real-time Updates

### Phase 4: Advanced Features
14. Cleanup & Maintenance
15. Platform Settings
16. Notifications
17. Export & Reporting

---

## Technical Recommendations

**Frontend Framework:**
- React 18+ with TypeScript
- Next.js for SSR (optional)
- State Management: Zustand or Redux Toolkit
- API Client: Axios or React Query
- UI Library: Material-UI, Ant Design, or Chakra UI
- Charts: Recharts or Chart.js
- Tables: TanStack Table (React Table v8)
- Forms: React Hook Form + Zod validation
- Date Handling: date-fns or Day.js

**Development Tools:**
- Vite for fast development
- ESLint + Prettier for code quality
- Storybook for component development
- Jest + React Testing Library for testing
- Cypress for E2E testing

**Deployment:**
- Static hosting (Vercel, Netlify, Cloudflare Pages)
- CDN for assets
- Environment-based configuration
- CI/CD pipeline

---

**Document Version:** 1.0  
**Last Updated:** November 28, 2025  
**Status:** Ready for Implementation

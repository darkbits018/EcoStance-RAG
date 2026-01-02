# Gmail-to-RAG Automation System - Architecture & Planning Document

## Overview
A comprehensive system to automatically fetch emails from specified recipients, process them through the existing RAG pipeline, and provide dynamic configuration for scheduling, recipient management, and system control. This system integrates seamlessly with the existing QuickShip architecture without duplicating functionality.

## Integration with Existing System

### Leveraging Current Architecture
- **Existing Services**: Utilize `scheduler_service.py`, `rag_service.py`, `tenant_service.py`
- **Database Models**: Extend existing tenant model with Gmail configuration
- **Agent Integration**: Make Gmail data available to QuickShip agents via knowledge base tools
- **Authentication**: Use existing tenant-based authentication and authorization
- **Monitoring**: Integrate with existing `metrics_service.py` and `llm_tracking_service.py`

## System Architecture

### Core Components (New)

#### 1. Gmail Integration Service (`app/services/gmail_service.py`)
- **Gmail API Client**: Handles OAuth authentication and API communication
- **Email Fetcher**: Retrieves emails based on recipient filters and search criteria
- **Thread Processor**: Manages email threads and conversation context
- **Content Extractor**: Processes email content, attachments, and metadata
- **Integration**: Uses existing `embedding_service.py` and `qdrant_service.py`

#### 2. Gmail Configuration Models (Extend existing models)
- **Tenant Gmail Settings**: Add gmail_config to existing Tenant model
- **Gmail Recipients**: New model for managing recipient lists per tenant
- **Gmail Schedules**: New model for scheduling configurations per tenant
- **Gmail Execution Logs**: Track sync operations using existing audit patterns

#### 3. Enhanced Scheduler Service (Extend existing)
- **Gmail Tasks**: Add Gmail sync tasks to existing `scheduler_service.py`
- **Dynamic Scheduling**: Extend current scheduler with Gmail-specific schedules
- **Per-Tenant Scheduling**: Leverage existing tenant-based task management

#### 4. RAG Integration (Use existing services)
- **Document Processing**: Use existing `data_processing_service.py` and `chunking_service.py`
- **Vector Storage**: Integrate with existing `qdrant_service.py` and tenant collections
- **Knowledge Base**: Create Gmail-specific knowledge bases per tenant
- **Agent Access**: Make Gmail data available via existing agent knowledge base tools

#### 5. Monitoring & Control (Extend existing)
- **Execution Tracking**: Use existing `audit_service.py` and `metrics_service.py`
- **Error Handling**: Integrate with existing error handling infrastructure
- **Performance Monitoring**: Extend existing monitoring with Gmail-specific metrics
- **Alerting**: Use existing `alerting_service.py` for notifications

## Functional Requirements

### 1. Recipient Management
- **Dynamic Recipient List**: Add/remove email addresses without system restart
- **Recipient Groups**: Organize recipients into logical groups (clients, vendors, team)
- **Per-Recipient Settings**: Custom filters and processing rules per recipient
- **Recipient Status**: Enable/disable individual recipients
- **Bulk Operations**: Import/export recipient lists

### 2. Email Filtering & Processing
- **Advanced Search Filters**: 
  - Date ranges (after/before specific dates)
  - Subject line keywords
  - Attachment presence
  - Email labels/folders
  - Read/unread status
- **Content Processing**:
  - Email body text extraction
  - HTML to plain text conversion
  - Attachment text extraction (PDFs, docs)
  - Thread conversation assembly
- **Deduplication**: Avoid processing same emails multiple times

### 3. Scheduling Configuration
- **Multiple Schedule Types**:
  - Interval-based (every X minutes/hours)
  - Daily at specific time
  - Weekly on specific days/times
  - Manual execution only
- **Schedule Management**:
  - Enable/disable schedules independently
  - Modify schedules without system restart
  - Multiple concurrent schedules
  - Schedule conflict resolution
- **Execution Windows**:
  - Business hours only options
  - Timezone-aware scheduling
  - Holiday/weekend exclusions

### 4. System Control
- **Global On/Off Switch**: Master control for all automation
- **Per-Schedule Control**: Individual schedule enable/disable
- **Per-Recipient Control**: Individual recipient enable/disable
- **Maintenance Mode**: Pause all operations for system maintenance
- **Emergency Stop**: Immediate halt of all operations

## Technical Architecture

## Database Schema Extensions

### 1. Extend Existing Tenant Model
```python
# Add to existing Tenant.settings JSON field:
{
    "gmail_config": {
        "enabled": true,
        "oauth_credentials": "encrypted_credentials",
        "default_kb_name": "gmail_emails",
        "processing_settings": {
            "include_attachments": true,
            "max_email_age_days": 365,
            "chunk_size": 1000
        }
    }
}
```

### 2. New Models (Following existing patterns)
```python
# app/models/gmail_recipient.py
class GmailRecipient(Base):
    __tablename__ = "gmail_recipients"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    email_address = Column(String(255), nullable=False)
    display_name = Column(String(255))
    group_name = Column(String(100))
    enabled = Column(Boolean, default=True)
    filters = Column(JSON, default=dict)  # Search filters, date ranges, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# app/models/gmail_schedule.py  
class GmailSchedule(Base):
    __tablename__ = "gmail_schedules"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    schedule_type = Column(String(50))  # 'interval', 'daily', 'weekly', 'manual'
    schedule_config = Column(JSON)  # Interval, time, days, etc.
    recipient_ids = Column(JSON)  # List of recipient IDs to process
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

# app/models/gmail_execution_log.py
class GmailExecutionLog(Base):
    __tablename__ = "gmail_execution_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    schedule_id = Column(String(36), ForeignKey("gmail_schedules.id"))
    recipient_id = Column(String(36), ForeignKey("gmail_recipients.id"))
    execution_type = Column(String(50))  # 'scheduled', 'manual'
    status = Column(String(50))  # 'success', 'failed', 'partial'
    emails_processed = Column(Integer, default=0)
    emails_added = Column(Integer, default=0)
    errors = Column(JSON)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration_ms = Column(Integer)
```

## Service Integration Strategy

### 1. Gmail Service (`app/services/gmail_service.py`)
```python
class GmailService:
    """Integrates with existing services for seamless email processing"""
    
    def __init__(self, tenant_id: str, db: Session):
        self.tenant_id = tenant_id
        self.db = db
        # Use existing services
        self.qdrant_service = get_qdrant_client()
        self.tenant_service = get_tenant_service(self.qdrant_service)
        self.embedding_service = load_embedding_model()
        self.data_processing_service = DataProcessingService()
        
    def sync_emails_for_recipient(self, recipient_id: str) -> Dict:
        """Sync emails and add to existing RAG pipeline"""
        # 1. Fetch emails using Gmail API
        # 2. Convert to Document objects
        # 3. Use existing chunking_service.py
        # 4. Use existing embedding_service.py  
        # 5. Store in tenant's Qdrant collection
        # 6. Log using existing audit_service.py
```

### 2. Enhanced Scheduler Service (Extend existing)
```python
# Add to existing scheduler_service.py
class SchedulerService:
    def _run_gmail_tasks(self):
        """Add Gmail sync tasks to existing scheduler"""
        # Get all active Gmail schedules
        # Execute based on schedule type
        # Use existing error handling and logging
        
    def _run_hourly_tasks(self):
        # Existing hourly tasks...
        # Add: Check for Gmail schedules due for execution
        
    def _run_daily_tasks(self):
        # Existing daily tasks...
        # Add: Gmail cleanup and maintenance
```

### 3. Agent Integration (Extend existing agent tools)
```python
# Add to quickship_agent/tools/knowledge_base_tools.py
def create_gmail_search_tool(tenant_id: str):
    """Create tool for searching Gmail knowledge base"""
    # Use existing KB search patterns
    # Search Gmail-specific collections
    # Return formatted results for agent
```

### 4. API Endpoints (New router)
```python
# app/routers/gmail_router.py
# Follow existing router patterns
# Use existing auth middleware
# Integrate with existing error handling
```

### 3. API Endpoints Design (Security-Enhanced)
```
Gmail Configuration (Admin/Manager Only):
GET    /api/v1/gmail/config                    - Get Gmail settings (tenant-scoped)
PUT    /api/v1/gmail/config                    - Update Gmail settings (admin only)
POST   /api/v1/gmail/oauth/authorize           - Initiate OAuth flow (admin only)
POST   /api/v1/gmail/oauth/callback            - Handle OAuth callback (admin only)
DELETE /api/v1/gmail/oauth/revoke              - Revoke OAuth access (admin only)

Recipient Management (Admin/Manager Only):
GET    /api/v1/gmail/recipients                - List recipients (tenant-scoped)
POST   /api/v1/gmail/recipients                - Add recipient (permission check)
PUT    /api/v1/gmail/recipients/{id}           - Update recipient (ownership check)
DELETE /api/v1/gmail/recipients/{id}           - Remove recipient (ownership check)
POST   /api/v1/gmail/recipients/bulk           - Bulk import (admin only)

Schedule Management (Admin/Manager Only):
GET    /api/v1/gmail/schedules                 - List schedules (tenant-scoped)
POST   /api/v1/gmail/schedules                 - Create schedule (permission check)
PUT    /api/v1/gmail/schedules/{id}            - Update schedule (ownership check)
DELETE /api/v1/gmail/schedules/{id}            - Delete schedule (ownership check)
POST   /api/v1/gmail/schedules/{id}/toggle     - Enable/disable (ownership check)

Execution Control (Admin/Manager Only):
POST   /api/v1/gmail/execute/manual            - Manual sync (permission check)
POST   /api/v1/gmail/execute/recipient/{id}    - Sync recipient (ownership check)
POST   /api/v1/gmail/execute/schedule/{id}     - Execute schedule (ownership check)

User Access (All Users with Gmail Access):
GET    /api/v1/gmail/search                    - Search emails (permission-filtered)
GET    /api/v1/gmail/knowledge-bases           - List Gmail KBs (access-filtered)

Monitoring (Admin/Manager Only):
GET    /api/v1/gmail/logs/executions           - Execution history (tenant-scoped)
GET    /api/v1/gmail/logs/access               - Access logs (permission-filtered)
GET    /api/v1/gmail/stats/summary             - Statistics (tenant-scoped)
GET    /api/v1/gmail/health                    - Health check (admin only)

Security Headers Required:
- Authorization: Bearer <tenant_token>
- X-Tenant-ID: <tenant_id>
- X-User-ID: <user_id>
- X-Request-ID: <correlation_id>
```

## Implementation Phases

### Phase 1: Core Infrastructure
1. Set up database schema and configuration storage
2. Implement Gmail API integration and authentication
3. Create basic email fetching and processing pipeline
4. Develop RAG integration layer
5. Build configuration management system

### Phase 2: Scheduling System
1. Implement scheduling engine with multiple strategies
2. Create schedule management APIs
3. Add execution logging and monitoring
4. Implement error handling and retry logic
5. Build manual execution capabilities

### Phase 3: Dynamic Configuration
1. Develop recipient management system
2. Create advanced filtering capabilities
3. Implement per-recipient custom settings
4. Build bulk operations for recipient management
5. Add recipient grouping functionality

### Phase 4: User Interface
1. Create web-based configuration dashboard
2. Implement recipient management UI
3. Build schedule configuration interface
4. Add monitoring and logging dashboard
5. Create system control panel

### Phase 5: Advanced Features
1. Add real-time email processing via webhooks
2. Implement advanced analytics and reporting
3. Create notification and alerting system
4. Add backup and restore capabilities
5. Implement audit logging and compliance features

## Security, Tenant Isolation & RBAC

### 1. Tenant Isolation (Critical)

#### Data Isolation
- **Qdrant Collections**: Gmail emails stored in tenant-specific collections using existing `tenant_service.get_collection_name()` pattern
- **Database Isolation**: All Gmail models include `tenant_id` foreign key with strict validation
- **Credential Isolation**: OAuth tokens encrypted with tenant-specific keys using existing `vault_service.py`
- **Processing Isolation**: All Gmail operations scoped by `tenant_id` with mandatory validation
- **Resource Limits**: Per-tenant quotas for email storage, processing frequency, and API usage

#### Cross-Tenant Prevention
- **Query Isolation**: All database queries include `tenant_id` filter (following existing patterns)
- **API Isolation**: All endpoints validate tenant ownership before operations
- **Collection Access**: Qdrant operations restricted to tenant's collections only
- **Audit Isolation**: Execution logs and metrics separated by tenant

### 2. Role-Based Access Control (RBAC)

#### Permission Levels (Extending existing tenant user roles)
```python
# Extend existing TenantUser model permissions
GMAIL_PERMISSIONS = {
    "gmail.admin": {
        "description": "Full Gmail configuration access",
        "actions": ["configure", "schedule", "recipients", "view_all", "execute"]
    },
    "gmail.manager": {
        "description": "Manage recipients and schedules",
        "actions": ["recipients", "schedule", "view_own", "execute"]
    },
    "gmail.user": {
        "description": "Search Gmail data only",
        "actions": ["search", "view_own"]
    },
    "gmail.viewer": {
        "description": "Read-only access to Gmail data",
        "actions": ["search"]
    }
}
```

#### Access Control Matrix
| Role | Configure OAuth | Manage Recipients | Create Schedules | Execute Sync | Search Emails | View Logs |
|------|----------------|-------------------|------------------|--------------|---------------|-----------|
| **Tenant Admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Gmail Admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Gmail Manager** | ❌ | ✅ | ✅ | ✅ | ✅ | Own Only |
| **Gmail User** | ❌ | ❌ | ❌ | ❌ | ✅ | Own Only |
| **Regular User** | ❌ | ❌ | ❌ | ❌ | ✅* | ❌ |

*Only if granted explicit access to Gmail knowledge bases

#### Permission Enforcement
- **API Level**: Use existing `AuthMiddleware` with Gmail-specific permission checks
- **Service Level**: All Gmail service methods validate user permissions
- **Agent Level**: Agent tools inherit user's Gmail permissions
- **UI Level**: Interface elements shown/hidden based on user permissions

### 3. Authentication & Authorization

#### OAuth Security
- **Tenant-Scoped OAuth**: Each tenant has separate OAuth app and credentials
- **Secure Storage**: OAuth tokens encrypted using existing `vault_service.py` with tenant-specific keys
- **Token Rotation**: Automatic refresh token rotation with audit logging
- **Scope Limitation**: Minimal required Gmail scopes (readonly for most operations)
- **Revocation Handling**: Graceful handling of revoked tokens with user notification

#### API Authentication
- **Existing Auth Stack**: Leverage current `AuthMiddleware` and tenant validation
- **Permission Validation**: Check Gmail-specific permissions on every request
- **Rate Limiting**: Use existing `RateLimitMiddleware` with Gmail-specific limits
- **Audit Logging**: All Gmail operations logged via existing `audit_service.py`

### 4. Data Protection & Privacy

#### Email Content Security
- **Encryption at Rest**: Email content encrypted in Qdrant using tenant-specific keys
- **Encryption in Transit**: All API communications use TLS 1.3
- **PII Handling**: Automatic detection and special handling of sensitive information
- **Data Minimization**: Only store necessary email metadata and content
- **Right to Deletion**: Support for complete email data removal per tenant/user

#### Compliance & Governance
- **Data Retention**: Configurable per-tenant email retention policies
- **GDPR Compliance**: Support for data export, deletion, and consent management
- **Audit Trail**: Complete audit log of all email access and operations
- **Data Classification**: Automatic classification of email sensitivity levels
- **Geographic Restrictions**: Respect tenant's data residency requirements

### 5. Enhanced Security Models

#### Gmail User Permissions (New Model)
```python
class GmailUserPermission(Base):
    __tablename__ = "gmail_user_permissions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("tenant_users.id"), nullable=False)
    permission_type = Column(String(50), nullable=False)  # 'admin', 'manager', 'user', 'viewer'
    email_filters = Column(JSON, default=dict)  # Restrict access to specific senders/domains
    granted_by = Column(String(36), ForeignKey("tenant_users.id"))
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    is_active = Column(Boolean, default=True)
```

#### Gmail Access Log (New Model)
```python
class GmailAccessLog(Base):
    __tablename__ = "gmail_access_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("tenant_users.id"), nullable=False)
    action = Column(String(100), nullable=False)  # 'search', 'configure', 'sync', etc.
    resource_type = Column(String(50))  # 'email', 'recipient', 'schedule'
    resource_id = Column(String(255))  # Specific email ID, recipient, etc.
    search_query = Column(String(1000), nullable=True)  # For search operations
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    success = Column(Boolean, default=True)
    error_message = Column(String(1000), nullable=True)
    accessed_at = Column(DateTime, default=datetime.utcnow)
```

### 6. Security Integration with Existing Services

#### Vault Service Integration
```python
# Use existing vault_service.py for credential management
class GmailVaultIntegration:
    def store_oauth_credentials(self, tenant_id: str, credentials: dict):
        # Store with tenant-specific encryption key
        vault_key = f"gmail_oauth_{tenant_id}"
        return vault_service.store_encrypted(vault_key, credentials, tenant_id)
    
    def retrieve_oauth_credentials(self, tenant_id: str):
        # Retrieve and decrypt with tenant key
        vault_key = f"gmail_oauth_{tenant_id}"
        return vault_service.retrieve_encrypted(vault_key, tenant_id)
```

#### Audit Service Integration
```python
# Extend existing audit_service.py for Gmail operations
def log_gmail_operation(tenant_id: str, user_id: str, action: str, details: dict):
    audit_service.log_operation(
        tenant_id=tenant_id,
        user_id=user_id,
        service="gmail",
        action=action,
        resource_type="email",
        details=details,
        ip_address=get_client_ip(),
        user_agent=get_user_agent()
    )
```

### 7. Security Validation & Enforcement

#### Request Validation Pipeline
1. **Authentication**: Validate user session via existing auth middleware
2. **Tenant Validation**: Ensure user belongs to requested tenant
3. **Permission Check**: Validate Gmail-specific permissions
4. **Resource Ownership**: Verify user can access specific Gmail resources
5. **Rate Limiting**: Apply Gmail-specific rate limits
6. **Audit Logging**: Log all operations for security monitoring

#### Security Middleware Stack
```python
# Gmail-specific security middleware
class GmailSecurityMiddleware:
    def validate_gmail_access(self, request, tenant_id: str, action: str):
        # 1. Check if Gmail is enabled for tenant
        # 2. Validate user has required Gmail permissions
        # 3. Check resource-level permissions
        # 4. Log access attempt
        # 5. Apply rate limiting
```

### 8. Monitoring & Alerting

#### Security Monitoring
- **Failed Authentication**: Alert on repeated OAuth failures
- **Permission Violations**: Alert on unauthorized access attempts
- **Unusual Activity**: Detect abnormal email access patterns
- **Data Exfiltration**: Monitor for bulk email downloads
- **Configuration Changes**: Alert on Gmail setting modifications

#### Compliance Monitoring
- **Data Retention**: Monitor and enforce retention policies
- **Access Patterns**: Track who accesses what emails when
- **Export Activities**: Log all data export operations
- **Deletion Requests**: Track data deletion compliance

## Monitoring & Observability

### 1. Metrics & KPIs
- Emails processed per recipient/schedule
- Processing success/failure rates
- System performance and response times
- API usage and rate limit monitoring
- Storage usage and growth trends

### 2. Alerting & Notifications
- Failed execution notifications
- System error alerts
- Performance degradation warnings
- Configuration change notifications
- Maintenance and update alerts

### 3. Logging Strategy
- Structured logging with correlation IDs
- Different log levels (DEBUG, INFO, WARN, ERROR)
- Centralized log aggregation
- Log retention and archival policies
- Real-time log monitoring and analysis

## Scalability & Performance

### 1. Performance Optimization
- Batch processing for multiple emails
- Parallel processing for multiple recipients
- Caching for frequently accessed data
- Database query optimization
- Efficient vector store operations

### 2. Scalability Considerations
- Horizontal scaling for processing workers
- Load balancing for API endpoints
- Database sharding for large datasets
- Queue-based processing for high volumes
- Resource monitoring and auto-scaling

## Integration Points

### 1. Existing RAG System Integration
- Document format compatibility
- Vector store integration
- Metadata schema alignment
- Search and retrieval optimization
- Performance impact assessment

### 2. External System Integration
- Gmail API and webhook integration
- Notification systems (email, Slack, etc.)
- Monitoring and alerting platforms
- Backup and storage systems
- Authentication providers

## Risk Assessment & Mitigation (Security-Enhanced)

### 1. Security Risks
- **OAuth Token Compromise**: Tokens could be stolen or misused
  - *Mitigation*: Encrypt tokens with tenant-specific keys, implement token rotation, monitor for unusual API usage
- **Cross-Tenant Data Leakage**: User accessing another tenant's emails
  - *Mitigation*: Strict tenant_id validation on all operations, separate Qdrant collections, comprehensive audit logging
- **Privilege Escalation**: User gaining unauthorized Gmail permissions
  - *Mitigation*: Role-based permission checks, permission inheritance validation, regular permission audits
- **Data Exfiltration**: Bulk download of sensitive emails
  - *Mitigation*: Rate limiting, access pattern monitoring, export logging, data loss prevention rules

### 2. Technical Risks
- **Gmail API Rate Limits**: Exceeding Google's API quotas
  - *Mitigation*: Implement exponential backoff, per-tenant rate limiting, quota monitoring and alerting
- **OAuth Revocation**: Users revoking Gmail access unexpectedly
  - *Mitigation*: Graceful error handling, user notification system, automatic retry with re-authorization
- **System Failures**: Service downtime affecting email processing
  - *Mitigation*: Circuit breakers, health checks, graceful degradation, comprehensive monitoring
- **Data Corruption**: Email data becoming corrupted during processing
  - *Mitigation*: Checksums, data validation, backup strategies, rollback capabilities

### 3. Compliance Risks
- **GDPR Violations**: Improper handling of EU user data
  - *Mitigation*: Data minimization, consent management, right to deletion, data residency controls
- **Data Retention Violations**: Keeping emails longer than allowed
  - *Mitigation*: Automated retention policies, regular cleanup jobs, compliance monitoring
- **Audit Failures**: Insufficient logging for compliance requirements
  - *Mitigation*: Comprehensive audit logging, tamper-proof logs, regular compliance reviews

### 4. Mitigation Implementation Strategy
- **Defense in Depth**: Multiple security layers (authentication, authorization, encryption, monitoring)
- **Principle of Least Privilege**: Users get minimum required permissions
- **Zero Trust Architecture**: Verify every request regardless of source
- **Continuous Monitoring**: Real-time security monitoring and alerting
- **Regular Security Reviews**: Periodic assessment of security posture and threat landscape

## Success Metrics

### 1. Functional Metrics
- Email processing accuracy (99%+)
- System uptime and availability (99.9%+)
- Configuration change success rate
- User satisfaction with interface
- Time to process new emails

### 2. Performance Metrics
- Average email processing time
- System response times for API calls
- Resource utilization efficiency
- Scalability under load
- Error rate and recovery time

This architecture provides a comprehensive, scalable, and maintainable solution for automated Gmail-to-RAG integration with full dynamic configuration capabilities.
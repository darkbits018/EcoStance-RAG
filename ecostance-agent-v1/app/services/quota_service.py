"""
Quota Service - Manages tenant resource quotas and usage tracking.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.models.tenant import Tenant

# === BEGIN: branch error handling ===
from ..core.logging import get_logger, log_error_with_context, log_operation_start, log_operation_success, log_operation_failure
from ..core.exceptions import QuotaExceededError, ResourceNotFoundError, DatabaseError, ValidationError
# === END: branch error handling ===

logger = get_logger(__name__)


# === BEGIN: branch error handling ===
# Legacy exception class kept for backward compatibility
class QuotaExceededException(Exception):
    """Exception raised when a tenant exceeds their quota."""
    def __init__(self, message: str, quota_type: str, current: int, limit: int):
        self.message = message
        self.quota_type = quota_type
        self.current = current
        self.limit = limit
        super().__init__(self.message)
# === END: branch error handling ===


class QuotaService:
    """Service for managing tenant quotas and usage tracking."""
    
    # Updated TIER_QUOTAS: Free Trial, Business, and Enterprise
    TIER_QUOTAS = {
        "free_trial": {
            "max_queries_per_day": 500,
            "max_queries_per_month": 15000,
            "max_documents": 5000,
            "max_storage_bytes": 5368709120,  # 5GB
            "max_db_connections": 2,
            "max_concurrent_queries": 5,
            "max_api_calls_per_minute": 30,
            "max_api_calls_per_hour": 1800,
        },
        "business": {
            "max_queries_per_day": 500,
            "max_queries_per_month": 15000,
            "max_documents": 5000,
            "max_storage_bytes": 5368709120,  # 5GB
            "max_db_connections": 2,
            "max_concurrent_queries": 5,
            "max_api_calls_per_minute": 30,
            "max_api_calls_per_hour": 1800,
        },
        "enterprise": {
            "max_queries_per_day": -1,  # Unlimited
            "max_queries_per_month": -1,
            "max_documents": -1,
            "max_storage_bytes": -1,
            "max_db_connections": 100,
            "max_concurrent_queries": 500,
            "max_api_calls_per_minute": 1000,
            "max_api_calls_per_hour": 60000,
        }
    }
    
    def __init__(self, db: Session):
        """Initialize quota service with database session."""
        self.db = db
    
    def get_tenant_quotas(self, tenant_id: str) -> Dict[str, int]:
        """
        Get quota limits for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Dictionary of quota limits
        """
        # === BEGIN: branch error handling ===
        try:
            if not tenant_id or not tenant_id.strip():
                raise ValidationError(
                    message="Tenant ID cannot be empty",
                    field="tenant_id"
                )
            
            log_operation_start(logger, "get_tenant_quotas", tenant_id=tenant_id)
            
            # Get tenant to determine tier
            try:
                tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
            except Exception as db_error:
                raise DatabaseError(
                    operation="tenant_lookup",
                    original_error=str(db_error)
                )
            
            if not tenant:
                raise ResourceNotFoundError(
                    resource_type="Tenant",
                    resource_id=tenant_id
                )
            
            # Check if custom quotas exist in database
            try:
                result = self.db.execute(
                    text("SELECT * FROM tenant_quotas WHERE tenant_id = :tenant_id"),
                    {"tenant_id": tenant_id}
                ).fetchone()
            except Exception as db_error:
                log_error_with_context(
                    logger=logger,
                    message="Failed to query custom quotas, using default quotas",
                    error=db_error,
                    extra_context={"tenant_id": tenant_id}
                )
                result = None
            
            if result:
                quotas = {
                    "max_queries_per_day": result[2],
                    "max_queries_per_month": result[3],
                    "max_documents": result[4],
                    "max_storage_bytes": result[5],
                    "max_db_connections": result[6],
                    "max_concurrent_queries": result[7],
                    "max_api_calls_per_minute": result[8],
                    "max_api_calls_per_hour": result[9],
                }
                log_operation_success(
                    logger, 
                    "get_tenant_quotas", 
                    quota_source="custom",
                    tenant_id=tenant_id
                )
                return quotas
            
            # Mapping of legacy tiers to new structure
            tier_map = {
                "free": "free_trial",
                "starter": "business",
                "professional": "business"
            }
            
            # Return default quotas based on tier
            raw_tier = tenant.billing_tier or "free_trial"
            tier = tier_map.get(raw_tier, raw_tier)
            
            # Final safety check for tier existence
            if tier not in self.TIER_QUOTAS:
                logger.warning(f"Unknown tier '{tier}' for tenant {tenant_id}. Falling back to free_trial.")
                tier = "free_trial"
                
            quotas = self.TIER_QUOTAS[tier]
            
            log_operation_success(
                logger, 
                "get_tenant_quotas", 
                quota_source="default",
                tier=tier,
                tenant_id=tenant_id
            )
            return quotas
            
        except (ValidationError, ResourceNotFoundError, DatabaseError):
            log_operation_failure(
                logger,
                "get_tenant_quotas",
                error=e,
                tenant_id=tenant_id
            )
            raise
        except Exception as e:
            log_operation_failure(
                logger,
                "get_tenant_quotas",
                error=e,
                remediation="Check database connectivity and tenant configuration",
                tenant_id=tenant_id
            )
            raise DatabaseError(
                operation="get_tenant_quotas",
                original_error=str(e)
            )
        # === END: branch error handling ===
    
    def get_current_usage(self, tenant_id: str, period_type: str = "daily") -> Dict[str, int]:
        """
        Get current usage for a tenant in the specified period.
        
        Args:
            tenant_id: Tenant identifier
            period_type: 'daily', 'monthly', or 'hourly'
            
        Returns:
            Dictionary of current usage values
        """
        # Calculate period boundaries
        now = datetime.utcnow()
        if period_type == "daily":
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period_type == "monthly":
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period_type == "hourly":
            period_start = now.replace(minute=0, second=0, microsecond=0)
        else:
            raise ValueError(f"Invalid period_type: {period_type}")
        
        # Query usage from database
        result = self.db.execute(
            text("""
            SELECT query_count, document_count, storage_bytes, 
                   active_db_connections, concurrent_queries, api_calls_count
            FROM tenant_quota_usage
            WHERE tenant_id = :tenant_id AND period_type = :period_type AND period_start = :period_start
            """),
            {"tenant_id": tenant_id, "period_type": period_type, "period_start": period_start}
        ).fetchone()
        
        if result:
            return {
                "query_count": result[0] or 0,
                "document_count": result[1] or 0,
                "storage_bytes": result[2] or 0,
                "active_db_connections": result[3] or 0,
                "concurrent_queries": result[4] or 0,
                "api_calls_count": result[5] or 0,
            }
        
        return {
            "query_count": 0,
            "document_count": 0,
            "storage_bytes": 0,
            "active_db_connections": 0,
            "concurrent_queries": 0,
            "api_calls_count": 0,
        }
    
    def check_query_quota(self, tenant_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if tenant can execute a query within quota limits.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Tuple of (allowed: bool, error_message: Optional[str])
        """
        # === BEGIN: branch error handling ===
        try:
            if not tenant_id or not tenant_id.strip():
                raise ValidationError(
                    message="Tenant ID cannot be empty",
                    field="tenant_id"
                )
            
            log_operation_start(logger, "check_query_quota", tenant_id=tenant_id)
            
            try:
                quotas = self.get_tenant_quotas(tenant_id)
                daily_usage = self.get_current_usage(tenant_id, "daily")
                monthly_usage = self.get_current_usage(tenant_id, "monthly")
            except Exception as e:
                log_error_with_context(
                    logger=logger,
                    message="Failed to get quota or usage data",
                    error=e,
                    extra_context={"tenant_id": tenant_id},
                    remediation="Check database connectivity and tenant configuration"
                )
                # Return conservative result - deny access if we can't check quotas
                return False, "Unable to verify quota limits. Please try again."
            
            # Check daily quota
            daily_limit = quotas["max_queries_per_day"]
            if daily_limit > 0 and daily_usage["query_count"] >= daily_limit:
                error_msg = f"Daily query quota exceeded ({daily_usage['query_count']}/{daily_limit})"
                logger.warning(
                    "Daily quota exceeded",
                    extra={
                        "tenant_id": tenant_id,
                        "current": daily_usage['query_count'],
                        "limit": daily_limit
                    }
                )
                return False, error_msg
            
            # Check monthly quota
            monthly_limit = quotas["max_queries_per_month"]
            if monthly_limit > 0 and monthly_usage["query_count"] >= monthly_limit:
                error_msg = f"Monthly query quota exceeded ({monthly_usage['query_count']}/{monthly_limit})"
                logger.warning(
                    "Monthly quota exceeded",
                    extra={
                        "tenant_id": tenant_id,
                        "current": monthly_usage['query_count'],
                        "limit": monthly_limit
                    }
                )
                return False, error_msg
            
            log_operation_success(
                logger,
                "check_query_quota",
                tenant_id=tenant_id,
                daily_usage=daily_usage["query_count"],
                monthly_usage=monthly_usage["query_count"]
            )
            return True, None
            
        except ValidationError:
            log_operation_failure(
                logger,
                "check_query_quota",
                error=e,
                tenant_id=tenant_id
            )
            raise
        except Exception as e:
            log_operation_failure(
                logger,
                "check_query_quota",
                error=e,
                remediation="Check database connectivity and quota configuration",
                tenant_id=tenant_id
            )
            # Return conservative result - deny access if quota check fails
            return False, "Unable to verify quota limits. Please try again."
        # === END: branch error handling ===
    
    def check_document_quota(self, tenant_id: str, additional_docs: int = 1) -> Tuple[bool, Optional[str]]:
        """
        Check if tenant can add more documents within quota limits.
        
        Args:
            tenant_id: Tenant identifier
            additional_docs: Number of documents to add
            
        Returns:
            Tuple of (allowed: bool, error_message: Optional[str])
        """
        quotas = self.get_tenant_quotas(tenant_id)
        usage = self.get_current_usage(tenant_id, "daily")
        
        doc_limit = quotas["max_documents"]
        if doc_limit > 0 and (usage["document_count"] + additional_docs) > doc_limit:
            return False, f"Document quota exceeded ({usage['document_count'] + additional_docs}/{doc_limit})"
        
        return True, None
    
    def check_storage_quota(self, tenant_id: str, additional_bytes: int = 0) -> Tuple[bool, Optional[str]]:
        """
        Check if tenant has enough storage quota.
        
        Args:
            tenant_id: Tenant identifier
            additional_bytes: Additional bytes to store
            
        Returns:
            Tuple of (allowed: bool, error_message: Optional[str])
        """
        quotas = self.get_tenant_quotas(tenant_id)
        usage = self.get_current_usage(tenant_id, "daily")
        
        storage_limit = quotas["max_storage_bytes"]
        if storage_limit > 0 and (usage["storage_bytes"] + additional_bytes) > storage_limit:
            used_gb = (usage["storage_bytes"] + additional_bytes) / (1024**3)
            limit_gb = storage_limit / (1024**3)
            return False, f"Storage quota exceeded ({used_gb:.2f}GB/{limit_gb:.2f}GB)"
        
        return True, None
    
    def check_connection_quota(self, tenant_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if tenant can create more database connections.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Tuple of (allowed: bool, error_message: Optional[str])
        """
        quotas = self.get_tenant_quotas(tenant_id)
        usage = self.get_current_usage(tenant_id, "daily")
        
        conn_limit = quotas["max_db_connections"]
        if conn_limit > 0 and usage["active_db_connections"] >= conn_limit:
            return False, f"Database connection quota exceeded ({usage['active_db_connections']}/{conn_limit})"
        
        return True, None
    
    def check_api_rate_limit(self, tenant_id: str, period: str = "minute") -> Tuple[bool, Optional[str]]:
        """
        Check if tenant is within API rate limits.
        
        Args:
            tenant_id: Tenant identifier
            period: 'minute' or 'hour'
            
        Returns:
            Tuple of (allowed: bool, error_message: Optional[str])
        """
        quotas = self.get_tenant_quotas(tenant_id)
        usage = self.get_current_usage(tenant_id, "hourly")
        
        if period == "minute":
            # For minute-based rate limiting, we'd need more granular tracking
            # For now, use hourly data as approximation
            limit = quotas["max_api_calls_per_minute"]
            current = usage["api_calls_count"] / 60  # Rough estimate
            if limit > 0 and current >= limit:
                return False, f"API rate limit exceeded ({int(current)}/{limit} per minute)"
        elif period == "hour":
            limit = quotas["max_api_calls_per_hour"]
            current = usage["api_calls_count"]
            if limit > 0 and current >= limit:
                return False, f"API rate limit exceeded ({current}/{limit} per hour)"
        
        return True, None
    
    def increment_usage(
        self,
        tenant_id: str,
        usage_type: str,
        amount: int = 1,
        period_type: str = "daily"
    ) -> None:
        """
        Increment usage counter for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            usage_type: Type of usage ('query', 'document', 'storage', 'connection', 'api_call')
            amount: Amount to increment
            period_type: 'daily', 'monthly', or 'hourly'
        """
        now = datetime.utcnow()
        
        # Calculate period boundaries
        if period_type == "daily":
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif period_type == "monthly":
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Calculate next month
            if period_start.month == 12:
                period_end = period_start.replace(year=period_start.year + 1, month=1)
            else:
                period_end = period_start.replace(month=period_start.month + 1)
        elif period_type == "hourly":
            period_start = now.replace(minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(hours=1)
        else:
            raise ValueError(f"Invalid period_type: {period_type}")
        
        # Map usage_type to column name
        column_map = {
            "query": "query_count",
            "document": "document_count",
            "storage": "storage_bytes",
            "connection": "active_db_connections",
            "concurrent_query": "concurrent_queries",
            "api_call": "api_calls_count",
        }
        
        column = column_map.get(usage_type)
        if not column:
            raise ValueError(f"Invalid usage_type: {usage_type}")
        
        # Insert or update usage record
        self.db.execute(
            text(f"""
            INSERT INTO tenant_quota_usage 
                (tenant_id, period_type, period_start, period_end, {column}, updated_at)
            VALUES (:tenant_id, :period_type, :period_start, :period_end, :amount, :now)
            ON CONFLICT(tenant_id, period_type, period_start) 
            DO UPDATE SET 
                {column} = {column} + :amount2,
                updated_at = :now2
            """),
            {"tenant_id": tenant_id, "period_type": period_type, "period_start": period_start, 
             "period_end": period_end, "amount": amount, "now": now, "amount2": amount, "now2": now}
        )
        self.db.commit()
        
        logger.debug(f"Incremented {usage_type} usage for tenant {tenant_id} by {amount}")
    
    def get_quota_status(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get comprehensive quota status for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Dictionary with quota limits, current usage, and percentages
        """
        quotas = self.get_tenant_quotas(tenant_id)
        daily_usage = self.get_current_usage(tenant_id, "daily")
        monthly_usage = self.get_current_usage(tenant_id, "monthly")
        
        def calc_percentage(current: int, limit: int) -> float:
            if limit <= 0:  # Unlimited
                return 0.0
            return (current / limit) * 100
        
        return {
            "tenant_id": tenant_id,
            "quotas": quotas,
            "daily_usage": {
                "queries": {
                    "current": daily_usage["query_count"],
                    "limit": quotas["max_queries_per_day"],
                    "percentage": calc_percentage(daily_usage["query_count"], quotas["max_queries_per_day"])
                },
                "api_calls": {
                    "current": daily_usage["api_calls_count"],
                    "limit": quotas["max_api_calls_per_hour"] * 24,
                    "percentage": calc_percentage(daily_usage["api_calls_count"], quotas["max_api_calls_per_hour"] * 24)
                }
            },
            "monthly_usage": {
                "queries": {
                    "current": monthly_usage["query_count"],
                    "limit": quotas["max_queries_per_month"],
                    "percentage": calc_percentage(monthly_usage["query_count"], quotas["max_queries_per_month"])
                }
            },
            "storage": {
                "current_bytes": daily_usage["storage_bytes"],
                "limit_bytes": quotas["max_storage_bytes"],
                "current_gb": daily_usage["storage_bytes"] / (1024**3),
                "limit_gb": quotas["max_storage_bytes"] / (1024**3) if quotas["max_storage_bytes"] > 0 else -1,
                "percentage": calc_percentage(daily_usage["storage_bytes"], quotas["max_storage_bytes"])
            },
            "connections": {
                "current": daily_usage["active_db_connections"],
                "limit": quotas["max_db_connections"],
                "percentage": calc_percentage(daily_usage["active_db_connections"], quotas["max_db_connections"])
            },
            "documents": {
                "current": daily_usage["document_count"],
                "limit": quotas["max_documents"],
                "percentage": calc_percentage(daily_usage["document_count"], quotas["max_documents"])
            }
        }
    
    def update_tenant_quotas(self, tenant_id: str, quotas: Dict[str, int]) -> None:
        """
        Update quota limits for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            quotas: Dictionary of quota values to update
        """
        from app.models.tenant_quota import TenantQuota
        
        # Verify tenant exists
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        # Get or create quota record
        quota_record = self.db.query(TenantQuota).filter(TenantQuota.tenant_id == tenant_id).first()
        if not quota_record:
            quota_record = TenantQuota(tenant_id=tenant_id)
            self.db.add(quota_record)
        
        # Map incoming quota keys to model fields
        # Note: QuotaService.TIER_QUOTAS uses "max_..." names
        field_map = {
            "max_queries_per_day": "queries_limit_daily",
            "max_queries_per_month": "queries_limit_monthly",
            "max_documents": "documents_limit",
            "max_storage_bytes": "storage_limit",
            "max_db_connections": "db_connections_limit"
        }
        
        for input_key, value in quotas.items():
            model_attr = field_map.get(input_key, input_key)
            if hasattr(quota_record, model_attr):
                # Ensure value is treated as an integer if it's a quota limit
                if value == -1: # Handle "Unlimited" logic if applicable
                    # Logic depends on how model handles -1, for now just set it
                    setattr(quota_record, model_attr, value)
                else:
                    setattr(quota_record, model_attr, value)
        
        quota_record.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Updated quotas for tenant {tenant_id}")

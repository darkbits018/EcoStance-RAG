"""
Custom exception classes for structured error handling.
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status


# === BEGIN: branch error handling ===
class BaseAppException(Exception):
    """Base exception class for application-specific errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "GENERIC_ERROR",
        details: Optional[Dict[str, Any]] = None,
        remediation: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.remediation = remediation
        super().__init__(self.message)


class ValidationError(BaseAppException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        remediation = kwargs.pop("remediation", "Please check your input and try again.")
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"field": field} if field else {},
            remediation=remediation,
            **kwargs
        )


class ResourceNotFoundError(BaseAppException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str, **kwargs):
        remediation = kwargs.pop("remediation", f"Please verify the {resource_type.lower()} ID and try again.")
        super().__init__(
            message=f"{resource_type} '{resource_id}' not found",
            error_code="RESOURCE_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id},
            remediation=remediation,
            **kwargs
        )


class QuotaExceededError(BaseAppException):
    """Raised when a tenant exceeds their quota limits."""
    
    def __init__(
        self,
        quota_type: str,
        current: int,
        limit: int,
        tenant_id: str,
        **kwargs
    ):
        remediation = kwargs.pop("remediation", "Please upgrade your plan or contact support for higher limits.")
        super().__init__(
            message=f"{quota_type} quota exceeded: {current}/{limit}",
            error_code="QUOTA_EXCEEDED",
            details={
                "quota_type": quota_type,
                "current": current,
                "limit": limit,
                "tenant_id": tenant_id
            },
            remediation=remediation,
            **kwargs
        )


class ExternalServiceError(BaseAppException):
    """Raised when external service calls fail."""
    
    def __init__(
        self,
        service_name: str,
        operation: str,
        original_error: Optional[str] = None,
        **kwargs
    ):
        remediation = kwargs.pop("remediation", "Please try again later. If the problem persists, contact support.")
        super().__init__(
            message=f"{service_name} service error during {operation}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details={
                "service_name": service_name,
                "operation": operation,
                "original_error": original_error
            },
            remediation=remediation,
            **kwargs
        )


class DatabaseError(BaseAppException):
    """Raised when database operations fail."""
    
    def __init__(self, operation: str, original_error: Optional[str] = None, **kwargs):
        remediation = kwargs.pop("remediation", "Please try again. If the problem persists, contact support.")
        super().__init__(
            message=f"Database error during {operation}",
            error_code="DATABASE_ERROR",
            details={"operation": operation, "original_error": original_error},
            remediation=remediation,
            **kwargs
        )


class AuthenticationError(BaseAppException):
    """Raised when authentication fails."""
    
    def __init__(self, reason: str = "Invalid credentials", **kwargs):
        remediation = kwargs.pop("remediation", "Please check your credentials and try again.")
        super().__init__(
            message=f"Authentication failed: {reason}",
            error_code="AUTHENTICATION_ERROR",
            details={"reason": reason},
            remediation=remediation,
            **kwargs
        )


class AuthorizationError(BaseAppException):
    """Raised when authorization fails."""
    
    def __init__(
        self,
        resource: str,
        action: str,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        remediation = kwargs.pop("remediation", "Please contact your administrator for access permissions.")
        super().__init__(
            message=f"Access denied: cannot {action} {resource}",
            error_code="AUTHORIZATION_ERROR",
            details={
                "resource": resource,
                "action": action,
                "tenant_id": tenant_id
            },
            remediation=remediation,
            **kwargs
        )


def convert_to_http_exception(exc: BaseAppException) -> HTTPException:
    """Convert application exception to FastAPI HTTPException."""
    
    status_code_map = {
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "RESOURCE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "QUOTA_EXCEEDED": status.HTTP_429_TOO_MANY_REQUESTS,
        "EXTERNAL_SERVICE_ERROR": status.HTTP_502_BAD_GATEWAY,
        "DATABASE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "AUTHENTICATION_ERROR": status.HTTP_401_UNAUTHORIZED,
        "AUTHORIZATION_ERROR": status.HTTP_403_FORBIDDEN,
        "GENERIC_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    status_code = status_code_map.get(exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "message": exc.message,
            "error_code": exc.error_code,
            "remediation": exc.remediation
        }
    )
# === END: branch error handling ===

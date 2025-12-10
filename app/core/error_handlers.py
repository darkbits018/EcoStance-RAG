"""
Global error handlers for FastAPI application.
"""
import logging
from typing import Union
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .exceptions import BaseAppException, convert_to_http_exception
from .logging import log_error_with_context, get_logger

logger = get_logger(__name__)


# === BEGIN: branch error handling ===
async def base_app_exception_handler(
    request: Request,
    exc: BaseAppException
) -> JSONResponse:
    """Handle custom application exceptions."""
    
    # Log the error with context
    log_error_with_context(
        logger=logger,
        message=f"Application error: {exc.message}",
        error=exc,
        extra_context={
            "error_code": exc.error_code,
            "details": exc.details,
            "path": str(request.url.path),
            "method": request.method
        },
        remediation=exc.remediation
    )
    
    # Convert to HTTP exception for consistent response format
    http_exc = convert_to_http_exception(exc)
    
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail
    )


async def http_exception_handler(
    request: Request,
    exc: Union[HTTPException, StarletteHTTPException]
) -> JSONResponse:
    """Handle HTTP exceptions with structured logging."""
    
    # Log non-client errors (5xx) as errors, client errors (4xx) as warnings
    if exc.status_code >= 500:
        log_error_with_context(
            logger=logger,
            message=f"HTTP {exc.status_code} error: {exc.detail}",
            extra_context={
                "status_code": exc.status_code,
                "path": str(request.url.path),
                "method": request.method
            },
            remediation="Internal server error occurred. Please try again or contact support."
        )
    else:
        logger.warning(
            f"HTTP {exc.status_code} client error: {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "path": str(request.url.path),
                "method": request.method
            }
        )
    
    # Ensure consistent response format
    detail = exc.detail
    if isinstance(detail, str):
        detail = {
            "message": detail,
            "error_code": f"HTTP_{exc.status_code}",
            "remediation": get_remediation_for_status(exc.status_code)
        }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=detail
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors."""
    
    # Extract validation error details
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error on {request.method} {request.url.path}",
        extra={
            "validation_errors": errors,
            "path": str(request.url.path),
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Request validation failed",
            "error_code": "VALIDATION_ERROR",
            "details": {"validation_errors": errors},
            "remediation": "Please check your request format and required fields."
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle all other unhandled exceptions."""
    
    # Log the unexpected error
    log_error_with_context(
        logger=logger,
        message=f"Unhandled exception: {type(exc).__name__}",
        error=exc,
        extra_context={
            "path": str(request.url.path),
            "method": request.method,
            "exception_type": type(exc).__name__
        },
        remediation="An unexpected error occurred. Please try again or contact support."
    )
    
    # Return generic error response (don't expose internal details)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "An unexpected error occurred",
            "error_code": "INTERNAL_SERVER_ERROR",
            "remediation": "Please try again. If the problem persists, contact support."
        }
    )


def get_remediation_for_status(status_code: int) -> str:
    """Get remediation message for HTTP status codes."""
    
    remediation_map = {
        400: "Please check your request format and try again.",
        401: "Please authenticate and try again.",
        403: "You don't have permission to access this resource.",
        404: "The requested resource was not found.",
        405: "This HTTP method is not allowed for this endpoint.",
        409: "There was a conflict with the current state of the resource.",
        422: "Please check your request data and try again.",
        429: "You've exceeded the rate limit. Please try again later.",
        500: "An internal server error occurred. Please try again or contact support.",
        502: "External service is unavailable. Please try again later.",
        503: "Service is temporarily unavailable. Please try again later.",
    }
    
    return remediation_map.get(
        status_code,
        "Please try again or contact support if the problem persists."
    )
# === END: branch error handling ===
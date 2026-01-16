"""
Request ID middleware for request tracing.
"""
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.logging import set_request_context, clear_request_context, get_logger

logger = get_logger(__name__)


# === BEGIN: branch error handling ===
class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to generate and track request IDs for tracing.
    
    This middleware:
    1. Generates a unique request ID for each request
    2. Sets request context for structured logging
    3. Adds request ID to response headers
    4. Measures request duration
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with ID tracking and context setting."""
        start_time = time.time()
        
        # Extract tenant info from existing auth middleware
        tenant_id = getattr(request.state, 'tenant_id', None)
        
        # Set request context for structured logging
        request_id = set_request_context(
            tenant_id=tenant_id,
            user_id=None  # Can be enhanced later with user info
        )
        
        # Add request ID to request state for easy access
        request.state.request_id = request_id
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Add headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms}ms"
            
            # Log successful request
            logger.info(
                f"Request completed: {request.method} {request.url.path}",
                extra={
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "path": str(request.url.path),
                    "method": request.method
                }
            )
            
            return response
            
        except Exception as e:
            # Calculate duration for failed requests
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log failed request
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "duration_ms": duration_ms,
                    "path": str(request.url.path),
                    "method": request.method
                },
                exc_info=True
            )
            
            # Re-raise the exception to be handled by error handlers
            raise
            
        finally:
            # Clear request context
            clear_request_context()
# === END: branch error handling ===
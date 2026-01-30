"""
Authentication middleware for tenant validation and request logging.
"""
import time
import logging
from typing import Callable, Optional
from fastapi import Request, Response, status, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError

from ..auth.jwt_handler import verify_token

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate tenant_id on every request and add logging.
    
    Excludes certain paths from authentication:
    - /docs, /redoc, /openapi.json (API documentation)
    - /health (health check)
    - / (root)
    """
    
    EXCLUDED_PATHS = [
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/api/v1/system/health",
        "/api/v1/auth/login",
        "/api/v1/auth/register"
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process each request, validate tenant, and log with tenant context.
        
        Supports JWT Bearer token authentication (Authorization: Bearer <token>)
        
        Args:
            request: Incoming request
            call_next: Next middleware/endpoint handler
            
        Returns:
            Response from the endpoint
        """
        start_time = time.time()
        
        # Skip authentication for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            response = await call_next(request)
            return response
        
        # Extract tenant_id from JWT token or header
        tenant_id = None
        auth_method = None
        auth_header = request.headers.get("Authorization")
        x_tenant_id = request.headers.get("X-Tenant-ID")
        
        # Try JWT token
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            try:
                payload = verify_token(token)
                tenant_id = payload.get("tenant_id")
                auth_method = "jwt"
            except JWTError as e:
                logger.warning(f"Invalid JWT token (JWTError): {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": f"Invalid authentication token: {str(e)}"},
                    headers={"WWW-Authenticate": "Bearer"}
                )
            except HTTPException as e:
                logger.error(f"Token verification error (HTTPException): {e.status_code}: {e.detail}")
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": e.detail},
                    headers={"WWW-Authenticate": "Bearer"}
                )
            except Exception as e:
                logger.error(f"Token verification error (Unknown): {type(e).__name__}: {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": f"Authentication error: {str(e)}"},
                    headers={"WWW-Authenticate": "Bearer"}
                )
        
        # Fallback to X-Tenant-ID header (for backward compatibility)
        elif x_tenant_id:
            tenant_id = x_tenant_id
            auth_method = "header"
            
        # REJECTION LOGIC: If no tenant_id is found for a non-excluded path, reject the request.
        if not tenant_id:
            logger.warning(
                f"Rejected unidentified request: {request.method} {request.url.path} | "
                f"Client: {request.client.host if request.client else 'Unknown'}"
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Identification required. Please provide a valid JWT token in the Authorization header or an X-Tenant-ID header.",
                    "error": "missing_identification"
                },
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Log request with tenant context
        logger.info(
            f"Request: {request.method} {request.url.path} | "
            f"Tenant: {tenant_id} | "
            f"Auth: {auth_method} | "
            f"Client: {request.client.host if request.client else 'Unknown'}"
        )
        
        # Add tenant_id and auth method to request state for easy access in endpoints
        request.state.tenant_id = tenant_id
        request.state.auth_method = auth_method
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(
                f"Request failed: {request.method} {request.url.path} | "
                f"Tenant: {tenant_id or 'None'} | "
                f"Error: {str(e)}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )
        
        # Log response with timing
        process_time = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Tenant: {tenant_id or 'None'} | "
            f"Time: {process_time:.3f}s"
        )
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(process_time)
        if tenant_id:
            response.headers["X-Tenant-ID"] = tenant_id
        
        return response

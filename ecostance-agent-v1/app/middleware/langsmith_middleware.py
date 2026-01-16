"""
LangSmith middleware for tracing HTTP requests.
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..services.langsmith_service import langsmith_service
import logging

logger = logging.getLogger(__name__)

class LangSmithMiddleware(BaseHTTPMiddleware):
    """Middleware to trace HTTP requests with LangSmith."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not langsmith_service.is_enabled():
            return await call_next(request)
        
        # Generate trace ID for this request
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id
        
        # Extract request info
        method = request.method
        url = str(request.url)
        path = request.url.path
        
        # Skip tracing for health checks and static files
        if path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        start_time = time.time()
        
        # Prepare trace inputs
        trace_inputs = {
            "method": method,
            "url": url,
            "path": path,
            "headers": dict(request.headers),
            "query_params": dict(request.query_params)
        }
        
        # Add user context if available
        if hasattr(request.state, "user_id"):
            trace_inputs["user_id"] = request.state.user_id
        if hasattr(request.state, "tenant_id"):
            trace_inputs["tenant_id"] = request.state.tenant_id
        
        with langsmith_service.trace_context(
            name=f"HTTP {method} {path}",
            inputs=trace_inputs,
            tags=["http", "api", method.lower()],
            extra={"trace_id": trace_id}
        ) as trace_run:
            try:
                # Process request
                response = await call_next(request)
                
                # Calculate duration
                duration = time.time() - start_time
                
                # Prepare trace outputs
                trace_outputs = {
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "success": 200 <= response.status_code < 400
                }
                
                # Add response headers (selective)
                response_headers = {}
                for header in ["content-type", "content-length"]:
                    if header in response.headers:
                        response_headers[header] = response.headers[header]
                trace_outputs["response_headers"] = response_headers
                
                # Update trace with outputs
                if trace_run:
                    langsmith_service.client.update_run(
                        run_id=trace_run.id,
                        outputs=trace_outputs
                    )
                
                # Add trace ID to response headers for debugging
                response.headers["X-Trace-ID"] = trace_id
                
                return response
                
            except Exception as e:
                # Log error in trace
                duration = time.time() - start_time
                error_outputs = {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": round(duration * 1000, 2),
                    "success": False
                }
                
                if trace_run:
                    langsmith_service.client.update_run(
                        run_id=trace_run.id,
                        outputs=error_outputs,
                        error=str(e)
                    )
                
                logger.error(f"Request failed with trace ID {trace_id}: {e}")
                raise
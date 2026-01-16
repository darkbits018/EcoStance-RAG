"""
Structured logging utilities with contextual information.
"""
import logging
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from contextvars import ContextVar


# === BEGIN: branch error handling ===
# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
tenant_id_var: ContextVar[Optional[str]] = ContextVar('tenant_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)


class StructuredFormatter(logging.Formatter):
    """Custom formatter that adds structured context to log records."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Get context variables
        request_id = request_id_var.get()
        tenant_id = tenant_id_var.get()
        user_id = user_id_var.get()
        
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from the log record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in [
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'getMessage', 'exc_info',
                'exc_text', 'stack_info'
            ]:
                extra_fields[key] = value
        
        if extra_fields:
            log_entry["extra"] = extra_fields
        
        return json.dumps(log_entry, default=str)


def setup_structured_logging(
    log_level: str = "INFO",
    enable_console: bool = True,
    enable_file: bool = True,
    error_file: str = "errorlog.txt"
) -> None:
    """Setup structured logging configuration."""
    
    # Create formatters
    structured_formatter = StructuredFormatter()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] [%(tenant_id)s] - %(message)s',
        defaults={'request_id': 'N/A', 'tenant_id': 'N/A'}
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler (human-readable)
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler for errors (structured JSON)
    if enable_file:
        file_handler = logging.FileHandler(error_file, mode='a')
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(structured_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with structured formatting capabilities."""
    return logging.getLogger(name)


def set_request_context(
    request_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> str:
    """Set context variables for the current request."""
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    request_id_var.set(request_id)
    tenant_id_var.set(tenant_id)
    user_id_var.set(user_id)
    
    return request_id


def clear_request_context() -> None:
    """Clear all context variables."""
    request_id_var.set(None)
    tenant_id_var.set(None)
    user_id_var.set(None)


def log_error_with_context(
    logger: logging.Logger,
    message: str,
    error: Optional[Exception] = None,
    extra_context: Optional[Dict[str, Any]] = None,
    remediation: Optional[str] = None
) -> None:
    """Log an error with full context and remediation hints."""
    
    context = {
        "error_type": type(error).__name__ if error else "Unknown",
        "error_message": str(error) if error else None,
        "remediation": remediation,
        **(extra_context or {})
    }
    
    logger.error(
        message,
        extra=context,
        exc_info=error is not None
    )


def log_operation_start(
    logger: logging.Logger,
    operation: str,
    **kwargs
) -> None:
    """Log the start of an operation with context."""
    logger.info(
        f"Starting operation: {operation}",
        extra={"operation": operation, "operation_status": "started", **kwargs}
    )


def log_operation_success(
    logger: logging.Logger,
    operation: str,
    duration_ms: Optional[int] = None,
    **kwargs
) -> None:
    """Log successful completion of an operation."""
    extra = {"operation": operation, "operation_status": "completed", **kwargs}
    if duration_ms is not None:
        extra["duration_ms"] = duration_ms
    
    logger.info(
        f"Operation completed successfully: {operation}",
        extra=extra
    )


def log_operation_failure(
    logger: logging.Logger,
    operation: str,
    error: Exception,
    duration_ms: Optional[int] = None,
    remediation: Optional[str] = None,
    **kwargs
) -> None:
    """Log failed operation with error details."""
    extra = {
        "operation": operation,
        "operation_status": "failed",
        "error_type": type(error).__name__,
        "error_message": str(error),
        "remediation": remediation,
        **kwargs
    }
    if duration_ms is not None:
        extra["duration_ms"] = duration_ms
    
    logger.error(
        f"Operation failed: {operation}",
        extra=extra,
        exc_info=True
    )
# === END: branch error handling ===
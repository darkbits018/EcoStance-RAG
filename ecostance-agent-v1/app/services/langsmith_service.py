"""
LangSmith tracing service for comprehensive system monitoring.
"""
import os
import uuid
from typing import Dict, Any, Optional, List
from functools import wraps
from contextlib import contextmanager
import asyncio
from datetime import datetime

from langsmith import Client
from langsmith.run_helpers import traceable
from langsmith.wrappers import wrap_openai
import logging

from ..config.langsmith_config import langsmith_config, should_trace_services

# Set up LangChain tracing environment variables
if langsmith_config.enabled:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = langsmith_config.api_key or ""
    os.environ["LANGCHAIN_PROJECT"] = langsmith_config.project_name

logger = logging.getLogger(__name__)

class LangSmithService:
    """Centralized LangSmith service for system-wide tracing."""
    
    def __init__(self):
        self.client = None
        self.config = langsmith_config
        
        if self.config.enabled:
            try:
                self.client = Client(
                    api_url=self.config.endpoint,
                    api_key=self.config.api_key
                )
                logger.info(f"LangSmith tracing enabled for project: {self.config.project_name}")
                logger.info(f"Tracing level: {self.config.tracing_level.value}")
            except Exception as e:
                logger.warning(f"Failed to initialize LangSmith client: {e}")
                self.config.enabled = False
        else:
            logger.info("LangSmith tracing disabled")
    
    def is_enabled(self) -> bool:
        """Check if LangSmith tracing is enabled."""
        return self.config.enabled and self.client is not None
    
    @contextmanager
    def trace_context(self, name: str, parent_run_id: Optional[str] = None, **kwargs):
        """Context manager for tracing operations with optional parent."""
        if not self.is_enabled():
            yield None
            return
        
        run_id = str(uuid.uuid4())
        try:
            # Start trace with optional parent
            run_kwargs = {
                "name": name,
                "run_type": "chain",
                "project_name": self.config.project_name,
                "inputs": kwargs.get("inputs", {}),
                "extra": kwargs.get("extra", {}),
                "tags": kwargs.get("tags", []),
                "id": run_id
            }
            
            # Add parent if provided
            if parent_run_id:
                run_kwargs["parent_run_id"] = parent_run_id
            
            run = self.client.create_run(**run_kwargs)
            yield run
        except Exception as e:
            logger.error(f"Error in trace context: {e}")
            yield None
        finally:
            try:
                if 'run' in locals():
                    self.client.update_run(
                        run_id=run_id,
                        outputs=kwargs.get("outputs", {}),
                        end_time=datetime.utcnow()
                    )
            except Exception as e:
                logger.error(f"Error updating run: {e}")
    
    def get_current_run_id(self):
        """Get the current run ID from context (if any)."""
        # This would need to be implemented with thread-local storage
        # For now, return None to keep existing behavior
        return getattr(self, '_current_run_id', None)
    
    def set_current_run_id(self, run_id: str):
        """Set the current run ID in context."""
        self._current_run_id = run_id
    
    def clear_current_run_id(self):
        """Clear the current run ID from context."""
        self._current_run_id = None
    
    def trace_function(self, name: Optional[str] = None, tags: Optional[List[str]] = None):
        """Decorator for tracing functions."""
        def decorator(func):
            if not self.is_enabled() or not should_trace_services():
                return func
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                trace_name = name or f"{func.__module__}.{func.__name__}"
                with self.trace_context(
                    name=trace_name,
                    inputs={"args": str(args)[:500], "kwargs": str(kwargs)[:500]},
                    tags=tags or []
                ):
                    try:
                        result = await func(*args, **kwargs)
                        return result
                    except Exception as e:
                        logger.error(f"Error in traced function {trace_name}: {e}")
                        raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                trace_name = name or f"{func.__module__}.{func.__name__}"
                with self.trace_context(
                    name=trace_name,
                    inputs={"args": str(args)[:500], "kwargs": str(kwargs)[:500]},
                    tags=tags or []
                ):
                    try:
                        result = func(*args, **kwargs)
                        return result
                    except Exception as e:
                        logger.error(f"Error in traced function {trace_name}: {e}")
                        raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def log_feedback(self, run_id: str, score: float, comment: Optional[str] = None):
        """Log feedback for a specific run."""
        if not self.is_enabled():
            return
        
        try:
            self.client.create_feedback(
                run_id=run_id,
                key="user_score",
                score=score,
                comment=comment
            )
        except Exception as e:
            logger.error(f"Error logging feedback: {e}")
    
    def create_dataset(self, name: str, description: Optional[str] = None):
        """Create a dataset for evaluation."""
        if not self.is_enabled():
            return None
        
        try:
            return self.client.create_dataset(
                dataset_name=name,
                description=description
            )
        except Exception as e:
            logger.error(f"Error creating dataset: {e}")
            return None
    
    def add_example_to_dataset(self, dataset_id: str, inputs: Dict[str, Any], outputs: Dict[str, Any]):
        """Add an example to a dataset."""
        if not self.is_enabled():
            return
        
        try:
            self.client.create_example(
                dataset_id=dataset_id,
                inputs=inputs,
                outputs=outputs
            )
        except Exception as e:
            logger.error(f"Error adding example to dataset: {e}")

# Global instance
langsmith_service = LangSmithService()

# Limited tracing decorators using LangSmith's @traceable for proper hierarchy
def trace_agent(func):
    """Specific decorator for agent functions."""
    if not langsmith_service.is_enabled() or not should_trace_services():
        return func
    return traceable(name=f"agent.{func.__name__}", tags=["agent", "ai"])(func)

def trace_rag(func):
    """Specific decorator for RAG functions."""
    if not langsmith_service.is_enabled() or not should_trace_services():
        return func
    return traceable(name=f"rag.{func.__name__}", tags=["rag", "retrieval"])(func)

def trace_llm(func):
    """Specific decorator for LLM functions."""
    if not langsmith_service.is_enabled() or not should_trace_services():
        return func
    return traceable(name=f"llm.{func.__name__}", tags=["llm", "generation"])(func)

def trace_embedding(func):
    """Specific decorator for embedding functions."""
    if not langsmith_service.is_enabled() or not should_trace_services():
        return func
    return traceable(name=f"embedding.{func.__name__}", tags=["embedding", "vectorization"])(func)
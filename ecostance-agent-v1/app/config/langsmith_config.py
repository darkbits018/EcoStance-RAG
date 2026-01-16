"""
LangSmith tracing configuration and utilities.
"""

import os
from typing import Dict, List, Optional
from enum import Enum

class TracingLevel(Enum):
    """Tracing levels for embedding, RAG, and agent operations only."""
    DISABLED = "disabled"
    BASIC = "basic"      # Core operations only
    STANDARD = "standard"  # Embedding + RAG + Agent
    DETAILED = "detailed"  # All functions with detailed context
    DEBUG = "debug"      # Maximum tracing for debugging

class LangSmithConfig:
    """Configuration class for LangSmith tracing."""
    
    def __init__(self):
        self.enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
        self.api_key = os.getenv("LANGCHAIN_API_KEY")
        self.project_name = os.getenv("LANGCHAIN_PROJECT", "ecostance-agent-v1")
        self.endpoint = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
        
        # Tracing level configuration
        level_str = os.getenv("LANGSMITH_TRACING_LEVEL", "standard").lower()
        try:
            self.tracing_level = TracingLevel(level_str)
        except ValueError:
            self.tracing_level = TracingLevel.STANDARD
        
        # Performance settings
        self.batch_size = int(os.getenv("LANGSMITH_BATCH_SIZE", "10"))
        self.flush_interval = int(os.getenv("LANGSMITH_FLUSH_INTERVAL", "5"))  # seconds
        
        # Filtering settings
        self.exclude_paths = self._parse_list(os.getenv("LANGSMITH_EXCLUDE_PATHS", "/health,/docs,/redoc,/openapi.json"))
        self.include_request_body = os.getenv("LANGSMITH_INCLUDE_REQUEST_BODY", "false").lower() == "true"
        self.include_response_body = os.getenv("LANGSMITH_INCLUDE_RESPONSE_BODY", "false").lower() == "true"
        self.max_body_size = int(os.getenv("LANGSMITH_MAX_BODY_SIZE", "1000"))  # characters
        
        # Sampling settings
        self.sampling_rate = float(os.getenv("LANGSMITH_SAMPLING_RATE", "1.0"))  # 0.0 to 1.0
        
    def _parse_list(self, value: str) -> List[str]:
        """Parse comma-separated string into list."""
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]
    
    def should_trace_path(self, path: str) -> bool:
        """Check if a path should be traced."""
        if not self.enabled:
            return False
        
        # Check exclusions
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return False
        
        return True
    
    def should_trace_level(self, level: TracingLevel) -> bool:
        """Check if tracing should be enabled for a specific level."""
        if not self.enabled:
            return False
        
        level_hierarchy = {
            TracingLevel.DISABLED: 0,
            TracingLevel.BASIC: 1,
            TracingLevel.STANDARD: 2,
            TracingLevel.DETAILED: 3,
            TracingLevel.DEBUG: 4
        }
        
        return level_hierarchy[self.tracing_level] >= level_hierarchy[level]
    
    def get_trace_tags(self, operation_type: str, **kwargs) -> List[str]:
        """Generate standardized tags for traces."""
        tags = [operation_type]
        
        # Add environment tag
        env = os.getenv("ENVIRONMENT", "development")
        tags.append(f"env:{env}")
        
        # Add service tags
        if "service" in kwargs:
            tags.append(f"service:{kwargs['service']}")
        
        # Add tenant tag if available
        if "tenant_id" in kwargs:
            tags.append(f"tenant:{kwargs['tenant_id']}")
        
        # Add user tag if available
        if "user_id" in kwargs:
            tags.append(f"user:{kwargs['user_id']}")
        
        return tags
    
    def get_metadata(self, **kwargs) -> Dict:
        """Generate standardized metadata for traces."""
        metadata = {
            "service": "ecostance-agent",
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "environment": os.getenv("ENVIRONMENT", "development")
        }
        
        # Add additional metadata
        metadata.update(kwargs)
        
        return metadata

# Global configuration instance
langsmith_config = LangSmithConfig()

# Convenience functions for limited tracing scope
def should_trace_services() -> bool:
    """Check if embedding, RAG, and agent services should be traced."""
    return langsmith_config.should_trace_level(TracingLevel.STANDARD)

def should_trace_functions() -> bool:
    """Check if individual functions should be traced."""
    return langsmith_config.should_trace_level(TracingLevel.DETAILED)

def should_trace_debug() -> bool:
    """Check if debug-level tracing should be enabled."""
    return langsmith_config.should_trace_level(TracingLevel.DEBUG)

# Limited tag generators - only for embedding, RAG, and agent
def get_rag_tags(**kwargs) -> List[str]:
    """Generate tags for RAG operations."""
    return langsmith_config.get_trace_tags("rag", **kwargs)

def get_agent_tags(**kwargs) -> List[str]:
    """Generate tags for agent operations."""
    return langsmith_config.get_trace_tags("agent", **kwargs)

def get_llm_tags(model: str = None, **kwargs) -> List[str]:
    """Generate tags for LLM operations."""
    tags = langsmith_config.get_trace_tags("llm", **kwargs)
    if model:
        tags.append(f"model:{model}")
    return tags

def get_embedding_tags(**kwargs) -> List[str]:
    """Generate tags for embedding operations."""
    return langsmith_config.get_trace_tags("embedding", **kwargs)
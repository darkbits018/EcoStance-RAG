"""
Multilingual Configuration for QuickShip AI Agent
Parallel configuration for multilingual features without disrupting existing system
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Multilingual Feature Flags ---
MULTILINGUAL_ENABLED = os.getenv("MULTILINGUAL_ENABLED", "false").lower() == "true"
EMBEDDING_MODEL_TYPE = os.getenv("EMBEDDING_MODEL_TYPE", "huggingface")  # huggingface or bge-m3
FALLBACK_TO_LEGACY = os.getenv("FALLBACK_TO_LEGACY", "true").lower() == "true"

# Tenant whitelist for multilingual features (comma-separated)
TENANT_MULTILINGUAL_WHITELIST = os.getenv("TENANT_MULTILINGUAL_WHITELIST", "").split(",")
TENANT_MULTILINGUAL_WHITELIST = [t.strip() for t in TENANT_MULTILINGUAL_WHITELIST if t.strip()]

# --- BGE-M3 Embedding Configuration ---
BGE_M3_MODEL_NAME = "BAAI/bge-m3"
BGE_M3_EMBEDDING_DIMENSION = 1024
BGE_M3_MAX_SEQUENCE_LENGTH = 8192
BGE_M3_BATCH_SIZE = int(os.getenv("BGE_M3_BATCH_SIZE", "32"))
BGE_M3_NORMALIZE = os.getenv("BGE_M3_NORMALIZE", "true").lower() == "true"
BGE_M3_DEVICE = os.getenv("BGE_M3_DEVICE", "auto")  # auto, cpu, cuda

# --- Language Detection Configuration ---
LANGUAGE_DETECTION_ENABLED = os.getenv("LANGUAGE_DETECTION_ENABLED", "true").lower() == "true"
LANGUAGE_DETECTION_MIN_CONFIDENCE = float(os.getenv("LANGUAGE_DETECTION_MIN_CONFIDENCE", "0.7"))
LANGUAGE_DETECTION_MIN_TEXT_LENGTH = int(os.getenv("LANGUAGE_DETECTION_MIN_TEXT_LENGTH", "10"))

# --- Cross-Language Retrieval Configuration ---
CROSS_LANGUAGE_ENABLED = os.getenv("CROSS_LANGUAGE_ENABLED", "true").lower() == "true"
SAME_LANGUAGE_BOOST = float(os.getenv("SAME_LANGUAGE_BOOST", "1.5"))  # Boost factor for same-language results
CROSS_LANGUAGE_MIN_SIMILARITY = float(os.getenv("CROSS_LANGUAGE_MIN_SIMILARITY", "0.6"))
MAX_CROSS_LANGUAGE_RESULTS = int(os.getenv("MAX_CROSS_LANGUAGE_RESULTS", "3"))

# --- Language Support Tiers ---
TIER_1_LANGUAGES = ["en", "es", "fr", "de", "pt"]  # Full support
TIER_2_LANGUAGES = ["it", "nl", "ru", "zh", "ja"]  # Basic support
TIER_3_LANGUAGES = []  # Detection only (auto-populated from BGE-M3 capabilities)

# --- Multilingual Collection Naming ---
MULTILINGUAL_COLLECTION_SUFFIX = "_ml"  # Suffix for multilingual collections

# --- Language Preference Configuration ---
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
SESSION_LANGUAGE_MEMORY = os.getenv("SESSION_LANGUAGE_MEMORY", "true").lower() == "true"
USER_LANGUAGE_PREFERENCE_TTL = int(os.getenv("USER_LANGUAGE_PREFERENCE_TTL", "86400"))  # 24 hours

# --- Performance Configuration ---
MULTILINGUAL_CACHE_ENABLED = os.getenv("MULTILINGUAL_CACHE_ENABLED", "true").lower() == "true"
MULTILINGUAL_CACHE_TTL = int(os.getenv("MULTILINGUAL_CACHE_TTL", "3600"))  # 1 hour
EMBEDDING_CACHE_SIZE = int(os.getenv("EMBEDDING_CACHE_SIZE", "1000"))

# --- Logging Configuration ---
MULTILINGUAL_LOG_LEVEL = os.getenv("MULTILINGUAL_LOG_LEVEL", "INFO")
LOG_LANGUAGE_DETECTION = os.getenv("LOG_LANGUAGE_DETECTION", "true").lower() == "true"
LOG_CROSS_LANGUAGE_RETRIEVAL = os.getenv("LOG_CROSS_LANGUAGE_RETRIEVAL", "true").lower() == "true"

def is_tenant_multilingual_enabled(tenant_id: str) -> bool:
    """Check if multilingual features are enabled for a specific tenant."""
    if not MULTILINGUAL_ENABLED:
        return False
    
    # If whitelist is empty, enable for all tenants
    if not TENANT_MULTILINGUAL_WHITELIST:
        return True
    
    return tenant_id in TENANT_MULTILINGUAL_WHITELIST

def get_multilingual_collection_name(tenant_id: str, kb_name: str) -> str:
    """Generate multilingual collection name for a tenant and knowledge base."""
    from app.services.tenant_service import TenantService
    
    # Use existing tenant service logic but add multilingual suffix
    base_name = f"{TenantService._sanitize_name(tenant_id)}_{TenantService._sanitize_name(kb_name)}"
    return f"{base_name}{MULTILINGUAL_COLLECTION_SUFFIX}"

def should_use_multilingual_service(tenant_id: str = None) -> bool:
    """Determine if multilingual service should be used."""
    if not MULTILINGUAL_ENABLED:
        return False
    
    if tenant_id and not is_tenant_multilingual_enabled(tenant_id):
        return False
    
    return True
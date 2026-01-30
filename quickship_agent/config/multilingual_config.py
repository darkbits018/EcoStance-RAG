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

# Note: Individual tenant control is now managed via the 'multilingual' feature 
# flag in the tenant.settings JSON in the database.

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
CROSS_LANGUAGE_MIN_SIMILARITY = float(os.getenv("CROSS_LANGUAGE_MIN_SIMILARITY", "0.4"))
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

def is_tenant_multilingual_enabled(tenant_id: str, db=None) -> bool:
    """
    Check if multilingual features are enabled for a specific tenant.
    
    This replaces the dual control (global flag + whitelist) with 
    global flag + specific tenant feature level check.
    """
    if not MULTILINGUAL_ENABLED:
        return False
    
    if not tenant_id:
        return False
        
    # Use provided session or create a temporary one
    close_session = False
    if db is None:
        try:
            # QuickShip agent imports from app.db.database
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
            from app.db.database import SessionLocal
            db = SessionLocal()
            close_session = True
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Could not initialize DB session for multilingual check: {e}")
            return False

    try:
        from app.models.tenant import Tenant
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return False
            
        settings = tenant.settings or {}
        features = settings.get("features", [])
        return "multilingual" in features
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error checking multilingual status for tenant {tenant_id}: {e}")
        return False
    finally:
        if close_session:
            db.close()

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
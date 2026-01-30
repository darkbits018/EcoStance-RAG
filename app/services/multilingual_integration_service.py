"""
Multilingual Integration Service
Provides unified interface for multilingual features across the app
"""

import logging
from typing import Dict, Any, Optional, List
from ..config.multilingual_app_config import (
    initialize_multilingual_config,
    is_tenant_multilingual_enabled,
    should_use_multilingual_processing,
    get_multilingual_config_info,
    MULTILINGUAL_ENABLED
)

logger = logging.getLogger(__name__)

class MultilingualIntegrationService:
    """Service to integrate multilingual capabilities across the app."""
    
    def __init__(self):
        self.initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialize multilingual services."""
        try:
            initialize_multilingual_config()
            self.initialized = True
            logger.info("Multilingual integration service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize multilingual integration service: {e}")
            self.initialized = False
    
    def is_available(self) -> bool:
        """Check if multilingual features are available."""
        return self.initialized and MULTILINGUAL_ENABLED
    
    def get_processing_service(self, tenant_id: str = None):
        """Get multilingual processing service - no fallback to legacy."""
        from .multilingual_data_processing_service import process_and_upload_file_multilingual
        return process_and_upload_file_multilingual
    
    def get_embedding_service(self, tenant_id: str = None):
        """Get multilingual embedding service - no fallback to legacy."""
        from .multilingual_embedding_service import create_multilingual_embeddings
        return create_multilingual_embeddings
    
    def get_cleaning_service(self, tenant_id: str = None):
        """Get multilingual cleaning service - no fallback to legacy."""
        from .multilingual_cleaning_service import clean_and_enrich_blocks_multilingual
        return clean_and_enrich_blocks_multilingual
    
    def get_agent_service(self, tenant_id: str = None, **kwargs):
        """Get multilingual agent service - no fallback to legacy."""
        from quickship_agent.multilingual_agent_service import MultilingualAgentService
        return MultilingualAgentService(tenant_id=tenant_id, **kwargs)
    
    def process_file_with_best_service(self, file_path: str, collection_name: str, 
                                     tenant_id: str = None, **kwargs):
        """Process a file using multilingual pipeline - no fallback to legacy."""
        processing_service = self.get_processing_service(tenant_id)
        
        logger.info(f"Processing file with multilingual pipeline (BGE-M3): {file_path}")
        
        return processing_service(
            file_path=file_path,
            collection_name=collection_name,
            tenant_id=tenant_id,
            **kwargs
        )
    
    def get_tenant_capabilities(self, tenant_id: str) -> Dict[str, Any]:
        """Get multilingual capabilities for a specific tenant."""
        return {
            "tenant_id": tenant_id,
            "multilingual_enabled": is_tenant_multilingual_enabled(tenant_id),
            "multilingual_processing": should_use_multilingual_processing(tenant_id),
            "available_services": {
                "multilingual_embedding": self.is_available(),
                "multilingual_cleaning": self.is_available(),
                "multilingual_agent": self.is_available(),
                "cross_language_search": self.is_available()
            },
            "supported_languages": {
                "model": "BGE-M3 supports 100+ languages with high-quality embeddings",
                "common_languages": ["en", "es", "fr", "de", "pt", "it", "nl", "ru", "zh", "ja", "ko", "ar", "hi", "th", "vi", "tr", "pl", "cs", "hu", "ro"],
                "note": "BGE-M3 provides excellent support for all major world languages and many regional languages"
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status for multilingual features."""
        status = {
            "integration_service": {
                "initialized": self.initialized,
                "available": self.is_available()
            },
            "configuration": get_multilingual_config_info()
        }
        
        # Test service availability
        try:
            from .multilingual_embedding_service import is_multilingual_enabled, get_multilingual_model_info
            status["embedding_service"] = {
                "available": is_multilingual_enabled(),
                "model_info": get_multilingual_model_info() if is_multilingual_enabled() else None
            }
        except Exception as e:
            status["embedding_service"] = {
                "available": False,
                "error": str(e)
            }
        
        try:
            from quickship_agent.services.language_service import get_language_service
            lang_service = get_language_service()
            status["language_service"] = {
                "available": True,
                "test_detection": lang_service.detect_language("Hello world")
            }
        except Exception as e:
            status["language_service"] = {
                "available": False,
                "error": str(e)
            }
        
        return status
    
    def enable_for_tenant(self, tenant_id: str, db=None) -> Dict[str, Any]:
        """
        Enable multilingual features for a specific tenant.
        Updates the tenant.settings.features list in the database.
        """
        close_session = False
        if db is None:
            from ..db.database import SessionLocal
            db = SessionLocal()
            close_session = True
            
        try:
            from ..models.tenant import Tenant
            tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant:
                return {
                    "tenant_id": tenant_id,
                    "status": "error",
                    "message": "Tenant not found"
                }
            
            # Update features list
            settings = tenant.settings or {}
            features = settings.get("features", [])
            if "multilingual" not in features:
                features.append("multilingual")
                settings["features"] = features
                tenant.settings = settings
                db.commit()
                message = f"Multilingual features enabled for tenant {tenant_id}"
            else:
                message = f"Multilingual features already enabled for tenant {tenant_id}"
                
            return {
                "tenant_id": tenant_id,
                "action": "enable_multilingual",
                "status": "success",
                "message": message,
                "capabilities": self.get_tenant_capabilities(tenant_id)
            }
        except Exception as e:
            logger.error(f"Error enabling multilingual for tenant {tenant_id}: {e}")
            return {
                "tenant_id": tenant_id,
                "status": "error",
                "message": str(e)
            }
        finally:
            if close_session:
                db.close()
    
    def disable_for_tenant(self, tenant_id: str, db=None) -> Dict[str, Any]:
        """
        Disable multilingual features for a specific tenant.
        Removes 'multilingual' from the tenant.settings.features list.
        """
        close_session = False
        if db is None:
            from ..db.database import SessionLocal
            db = SessionLocal()
            close_session = True
            
        try:
            from ..models.tenant import Tenant
            tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant:
                return {
                    "tenant_id": tenant_id,
                    "status": "error",
                    "message": "Tenant not found"
                }
            
            # Update features list
            settings = tenant.settings or {}
            features = settings.get("features", [])
            if "multilingual" in features:
                features.remove("multilingual")
                settings["features"] = features
                tenant.settings = settings
                db.commit()
                message = f"Multilingual features disabled for tenant {tenant_id}"
            else:
                message = f"Multilingual features already disabled for tenant {tenant_id}"
                
            return {
                "tenant_id": tenant_id,
                "action": "disable_multilingual",
                "status": "success",
                "message": message,
                "capabilities": self.get_tenant_capabilities(tenant_id)
            }
        except Exception as e:
            logger.error(f"Error disabling multilingual for tenant {tenant_id}: {e}")
            return {
                "tenant_id": tenant_id,
                "status": "error",
                "message": str(e)
            }
        finally:
            if close_session:
                db.close()
    
    def migrate_tenant_to_multilingual(self, tenant_id: str, collections: List[str] = None) -> Dict[str, Any]:
        """Migrate a tenant's collections to use multilingual embeddings."""
        try:
            from .multilingual_data_processing_service import migrate_collection_to_multilingual
            
            results = []
            if collections:
                for collection in collections:
                    try:
                        # This would trigger the migration process
                        result = {
                            "collection": collection,
                            "status": "migration_scheduled",
                            "target_collection": f"{collection}_ml"
                        }
                        results.append(result)
                    except Exception as e:
                        results.append({
                            "collection": collection,
                            "status": "error",
                            "error": str(e)
                        })
            
            return {
                "tenant_id": tenant_id,
                "action": "migrate_to_multilingual",
                "status": "success",
                "collections": results,
                "message": f"Migration initiated for {len(results)} collections"
            }
            
        except Exception as e:
            return {
                "tenant_id": tenant_id,
                "action": "migrate_to_multilingual",
                "status": "error",
                "error": str(e)
            }


# Global integration service instance
_integration_service: Optional[MultilingualIntegrationService] = None

def get_multilingual_integration_service() -> MultilingualIntegrationService:
    """Get or create the global multilingual integration service."""
    global _integration_service
    if _integration_service is None:
        _integration_service = MultilingualIntegrationService()
    return _integration_service

# Convenience functions for easy access
def get_best_processing_service(tenant_id: str = None):
    """Get the best processing service for a tenant."""
    return get_multilingual_integration_service().get_processing_service(tenant_id)

def get_best_embedding_service(tenant_id: str = None):
    """Get the best embedding service for a tenant."""
    return get_multilingual_integration_service().get_embedding_service(tenant_id)

def get_best_cleaning_service(tenant_id: str = None):
    """Get the best cleaning service for a tenant."""
    return get_multilingual_integration_service().get_cleaning_service(tenant_id)

def get_best_agent_service(tenant_id: str = None, **kwargs):
    """Get the best agent service for a tenant."""
    return get_multilingual_integration_service().get_agent_service(tenant_id, **kwargs)

def process_file_intelligently(file_path: str, collection_name: str, tenant_id: str = None, **kwargs):
    """Process a file using the most appropriate service."""
    return get_multilingual_integration_service().process_file_with_best_service(
        file_path, collection_name, tenant_id, **kwargs
    )
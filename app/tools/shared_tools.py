"""
Shared tools for all agents.
This file contains generic tools that apply across different agent types,
such as knowledge base searching and listing.
"""
import logging
from langchain.tools import tool

logger = logging.getLogger(__name__)

def create_search_knowledge_base_tool(tenant_id: str):
    """
    Create a tenant-specific knowledge base search tool.
    
    Args:
        tenant_id: The tenant ID to scope the search to
    
    Returns:
        A tool function that searches the tenant's knowledge bases
    """
    @tool
    def search_knowledge_base(kb_name: str, query: str) -> str:
        """
        Search through company knowledge base documents for information.
        Use this when user asks about policies, procedures, FAQs, or general information.
        
        Args:
            kb_name: The name of the knowledge base to search. If you don't know the exact name, use 'list_available_knowledge_bases' FIRST.
            query: The question or search query
        
        Returns:
            Relevant information from the knowledge base documents
        """
        try:
            # Import here to avoid circular dependencies
            from app.services.query_service import execute_query
            from app.services.qdrant_service import get_qdrant_client
            from app.services.tenant_service import get_tenant_service
            from app.services.language_service import get_language_service
            from app.config.multilingual_app_config import MULTILINGUAL_ENABLED, MULTILINGUAL_COLLECTION_SUFFIX
            
            # Get services
            qdrant_client = get_qdrant_client()
            tenant_service = get_tenant_service(qdrant_client)
            language_service = get_language_service()
            
            # 1. Try multilingual collection first if enabled
            collection_name = None
            is_multilingual = False
            
            if MULTILINGUAL_ENABLED:
                ml_collection = f"{tenant_service.get_collection_name(tenant_id, kb_name)}{MULTILINGUAL_COLLECTION_SUFFIX}"
                if tenant_service.collection_exists(ml_collection):
                    collection_name = ml_collection
                    is_multilingual = True
            
            # 2. Fall back to standard collection
            if not collection_name:
                collection_name = tenant_service.get_collection_name(tenant_id, kb_name)
            
            logger.info(f"Searching KB '{kb_name}' (ML: {is_multilingual}) for tenant {tenant_id}, collection: {collection_name}")
            
            # 3. Detect language for context
            query_lang = language_service.detect_language(query)
            lang_name = language_service.get_language_name(query_lang)
            
            # 4. Execute RAG query (already uses BGE-M3 if configured)
            answer = execute_query(collection_name, query, chat_history=[])
            
            kb_label = f"{kb_name} ({lang_name})" if is_multilingual else kb_name
            return f"Knowledge Base {kb_label}:\n{answer}"
            
        except Exception as e:
            logger.error(f"Error in search_knowledge_base: {e}")
            from app.core.exceptions import ResourceNotFoundError, BaseAppException
            
            error_str = str(e)
            if isinstance(e, ResourceNotFoundError) or "Not found" in error_str or "doesn't exist" in error_str:
                return f"Error: Knowledge base '{kb_name}' does not exist. You MUST use 'list_available_knowledge_bases' to see the actual names of available knowledge bases for this tenant before searching again."
            
            if isinstance(e, BaseAppException) and e.remediation:
                return f"I couldn't search the knowledge base. Error: {e.message}. Remediation: {e.remediation}"
                
            return f"I couldn't search the knowledge base. Error: {error_str}"
    
    return search_knowledge_base


def create_list_knowledge_bases_tool(tenant_id: str):
    """
    Create a tenant-specific knowledge base listing tool.
    
    Args:
        tenant_id: The tenant ID to scope the listing to
    
    Returns:
        A tool function that lists the tenant's knowledge bases
    """
    @tool
    def list_available_knowledge_bases() -> str:
        """
        List all available knowledge bases that can be searched.
        Use this when you need to know what knowledge bases are available.
        
        Returns:
            List of available knowledge base names
        """
        try:
            # Import here to avoid circular dependencies
            from app.services.qdrant_service import get_qdrant_client
            from app.services.tenant_service import get_tenant_service
            from app.config.multilingual_app_config import MULTILINGUAL_COLLECTION_SUFFIX
            
            client = get_qdrant_client()
            tenant_service = get_tenant_service(client)
            
            # Get all collections
            collections = client.get_collections()
            
            if not collections.collections:
                return "No knowledge bases are currently available."
            
            # Filter for tenant-specific collections
            tenant_kbs = {} # kb_name -> [types]
            sanitized_tenant = tenant_service._sanitize_name(tenant_id)
            
            for col in collections.collections:
                parsed = tenant_service.parse_collection_name(col.name)
                if parsed and parsed["tenant_id"] == sanitized_tenant:
                    kb_name = parsed["kb_name"]
                    
                    if kb_name.endswith(MULTILINGUAL_COLLECTION_SUFFIX):
                        actual_name = kb_name[:-len(MULTILINGUAL_COLLECTION_SUFFIX)]
                        if actual_name not in tenant_kbs: tenant_kbs[actual_name] = []
                        tenant_kbs[actual_name].append("Multilingual")
                    else:
                        if kb_name not in tenant_kbs: tenant_kbs[kb_name] = []
                        tenant_kbs[kb_name].append("Standard")
            
            if not tenant_kbs:
                return "No knowledge bases are currently available for your organization."
            
            # Format nicely
            kb_list = []
            for name, types in sorted(tenant_kbs.items()):
                types_str = "/".join(sorted(types, reverse=True))
                kb_list.append(f"{name} ({types_str})")
            
            return f"Available knowledge bases: {', '.join(kb_list)}"
            
        except Exception as e:
            logger.error(f"Error in list_available_knowledge_bases: {e}")
            return f"Error listing knowledge bases: {str(e)}"
    
    return list_available_knowledge_bases

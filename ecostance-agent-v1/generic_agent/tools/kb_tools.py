"""
Knowledge Base Tools for Generic Agent
"""
import logging
from langchain.tools import tool

logger = logging.getLogger(__name__)

def create_search_knowledge_base_tool(tenant_id: str):
    @tool
    def search_knowledge_base(kb_name: str, query: str) -> str:
        """
        Search through company knowledge base documents for information.
        Useful for answering FAQs, policies, and general info.
        """
        try:
            # Reusing existing RAG logic from quickship_agent if compatible, 
            # or pointing to a shared service.
            from quickship_agent.services.rag_service import execute_query
            from quickship_agent.services.qdrant_service import get_qdrant_client
            from app.services.tenant_service import get_tenant_service
            
            qdrant_client = get_qdrant_client()
            tenant_service = get_tenant_service(qdrant_client)
            collection_name = tenant_service.get_collection_name(tenant_id, kb_name)
            
            logger.info(f"Generic Agent searching KB '{kb_name}' for tenant {tenant_id}")
            answer = execute_query(collection_name, query, chat_history=[])
            return f"Information from {kb_name}:\n{answer}"
        except Exception as e:
            logger.error(f"Error in generic search_knowledge_base: {e}")
            return f"Error searching knowledge base: {str(e)}"
    
    return search_knowledge_base

def create_list_knowledge_bases_tool(tenant_id: str):
    @tool
    def list_available_knowledge_bases() -> str:
        """List all available knowledge bases."""
        try:
            from quickship_agent.services.qdrant_service import get_qdrant_client
            from app.services.tenant_service import get_tenant_service
            
            client = get_qdrant_client()
            tenant_service = get_tenant_service(client)
            
            collections = client.get_collections()
            tenant_kbs = []
            sanitized_tenant = tenant_service._sanitize_name(tenant_id)
            
            for col in collections.collections:
                parsed = tenant_service.parse_collection_name(col.name)
                if parsed and parsed["tenant_id"] == sanitized_tenant:
                    tenant_kbs.append(parsed["kb_name"])
            
            if not tenant_kbs:
                return "No knowledge bases available."
            return f"Available knowledge bases: {', '.join(tenant_kbs)}"
        except Exception as e:
            return f"Error listing KBs: {str(e)}"
            
    return list_available_knowledge_bases

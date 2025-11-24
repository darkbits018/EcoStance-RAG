"""
Knowledge Base Tools for QuickShip Logistics
These tools allow the ReAct agent to search through company documents using RAG.
"""

import logging
from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool
def search_knowledge_base(collection_name: str, query: str) -> str:
    """
    Search through company knowledge base documents for information.
    Use this when customer asks about policies, procedures, FAQs, or general information
    that is not in the shipment database.
    
    Args:
        collection_name: The knowledge base to search (e.g., 'policies', 'faq', 'procedures')
        query: The question or search query
    
    Returns:
        Relevant information from the knowledge base documents
    """
    try:
        # Import here to avoid circular dependencies
        from ..services.rag_service import execute_query
        
        # Execute RAG query
        answer = execute_query(collection_name, query, chat_history=[])
        
        return f"Knowledge Base ({collection_name}):\n{answer}"
        
    except Exception as e:
        logger.error(f"Error in search_knowledge_base: {e}")
        return f"I couldn't search the knowledge base. Error: {str(e)}"


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
        from ..services.qdrant_service import get_qdrant_client
        
        client = get_qdrant_client()
        collections = client.get_collections()
        
        if not collections.collections:
            return "No knowledge bases are currently available."
        
        kb_list = [col.name for col in collections.collections]
        return f"Available knowledge bases: {', '.join(kb_list)}"
        
    except Exception as e:
        logger.error(f"Error in list_available_knowledge_bases: {e}")
        return f"Error listing knowledge bases: {str(e)}"

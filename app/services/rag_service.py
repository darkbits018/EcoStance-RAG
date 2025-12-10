"""
RAG Service - Wrapper for querying knowledge bases.
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import logging
import time

from ..models.tenant_knowledge_base import TenantKnowledgeBase
from ..services.query_service import execute_query, get_retriever, format_docs
from ..services.qdrant_service import get_qdrant_client
from ..services.tenant_service import get_tenant_service
from ..services.llm_tracking_service import LLMTrackingService
from ..services.cache_service import cache_get, cache_set

logger = logging.getLogger(__name__)


class RAGService:
    """Service for querying knowledge bases using RAG."""

    def __init__(self, db: Session):
        self.db = db

    async def query_knowledge_base(
        self,
        tenant_id: str,
        kb_id: str,
        query: str,
        top_k: int = 3,
        chat_history: Optional[List] = None
    ) -> Dict:
        """
        Query a knowledge base and return answer with sources.
        
        Args:
            tenant_id: Tenant ID
            kb_id: Knowledge base ID (kb_name)
            query: User query
            top_k: Number of top results to return
            chat_history: Optional conversation history
            
        Returns:
            Dictionary with answer and sources
        """
        try:
            # Check cache first (only for queries without chat history)
            if not chat_history:
                cached_result = cache_get(tenant_id, kb_id, query, top_k=top_k)
                if cached_result is not None:
                    logger.info(f"Cache HIT for query: '{query[:50]}...'")
                    return cached_result
            # Verify KB exists and belongs to tenant
            kb = self.db.query(TenantKnowledgeBase).filter(
                TenantKnowledgeBase.tenant_id == tenant_id,
                TenantKnowledgeBase.kb_id == kb_id
            ).first()

            if not kb:
                raise ValueError(f"Knowledge base {kb_id} not found for tenant {tenant_id}")

            # Generate tenant-specific collection name
            qdrant_client = get_qdrant_client()
            tenant_service = get_tenant_service(qdrant_client)
            collection_name = tenant_service.get_collection_name(tenant_id, kb.name)
            
            logger.info(f"Querying collection: {collection_name} for tenant: {tenant_id}, kb: {kb.name}")

            # Verify collection exists
            if not tenant_service.collection_exists(collection_name):
                raise ValueError(f"Collection {collection_name} not found in Qdrant")

            # Execute RAG query with tracking
            start_time = time.time()
            answer = execute_query(
                collection_name=collection_name,
                query=query,
                chat_history=chat_history or [],
                tenant_id=tenant_id
            )
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Track LLM usage (RAG uses embeddings + LLM for answer generation)
            try:
                # Estimate tokens (rough approximation: 1 token ≈ 4 chars)
                input_tokens = len(query) // 4
                output_tokens = len(answer) // 4
                
                LLMTrackingService.track_llm_call(
                    db=self.db,
                    tenant_id=str(tenant_id),
                    model="text-embedding-3-small",  # Default embedding model
                    operation_type='rag',
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    success=True,
                    latency_ms=latency_ms,
                    endpoint='/api/v1/query'
                )
            except Exception as track_error:
                logger.warning(f"Failed to track LLM usage: {track_error}")

            # Get source documents
            retriever = get_retriever(collection_name)
            docs = retriever.invoke(query)

            # Format sources
            sources = []
            for i, doc in enumerate(docs[:top_k]):
                source_info = {
                    "filename": doc.metadata.get("source", "Unknown"),
                    "chunk_number": i + 1,
                    "similarity": doc.metadata.get("score", 0.0),
                    "preview": doc.page_content[:200] if doc.page_content else ""
                }
                sources.append(source_info)

            result = {
                "answer": answer,
                "sources": sources,
                "kb_id": kb_id
            }
            
            # Cache the result (only for queries without chat history)
            if not chat_history:
                cache_set(tenant_id, kb_id, query, result, top_k=top_k)
                logger.debug(f"Cached result for query: '{query[:50]}...'")
            
            return result

        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}", exc_info=True)
            return {
                "answer": "I'm sorry, I encountered an error while processing your question. Please try again.",
                "sources": [],
                "error": str(e)
            }

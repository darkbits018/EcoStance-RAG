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

# === BEGIN: branch error handling ===
from ..core.logging import get_logger, log_error_with_context, log_operation_start, log_operation_success, log_operation_failure
from ..core.exceptions import ResourceNotFoundError, ValidationError, DatabaseError, ExternalServiceError
# === END: branch error handling ===

logger = get_logger(__name__)


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
        # === BEGIN: branch error handling ===
        start_time = time.time()
        
        try:
            # Input validation
            if not tenant_id or not tenant_id.strip():
                raise ValidationError(
                    message="Tenant ID cannot be empty",
                    field="tenant_id"
                )
            
            if not kb_id or not kb_id.strip():
                raise ValidationError(
                    message="Knowledge base ID cannot be empty",
                    field="kb_id"
                )
            
            if not query or not query.strip():
                raise ValidationError(
                    message="Query cannot be empty",
                    field="query"
                )
            
            if top_k <= 0:
                raise ValidationError(
                    message="top_k must be a positive integer",
                    field="top_k"
                )
            
            log_operation_start(
                logger,
                "query_knowledge_base",
                tenant_id=tenant_id,
                kb_id=kb_id,
                query_length=len(query),
                top_k=top_k,
                has_chat_history=bool(chat_history)
            )
            
            # Check cache first (only for queries without chat history)
            if not chat_history:
                try:
                    cached_result = cache_get(tenant_id, kb_id, query, top_k=top_k)
                    if cached_result is not None:
                        logger.info(
                            "Cache HIT for query",
                            extra={
                                "query_preview": query[:50],
                                "tenant_id": tenant_id,
                                "kb_id": kb_id
                            }
                        )
                        return cached_result
                except Exception as cache_error:
                    log_error_with_context(
                        logger=logger,
                        message="Cache lookup failed, continuing without cache",
                        error=cache_error,
                        extra_context={"tenant_id": tenant_id, "kb_id": kb_id}
                    )
            
            # Verify KB exists and belongs to tenant
            try:
                kb = self.db.query(TenantKnowledgeBase).filter(
                    TenantKnowledgeBase.tenant_id == tenant_id,
                    TenantKnowledgeBase.kb_id == kb_id
                ).first()
            except Exception as db_error:
                raise DatabaseError(
                    operation="knowledge_base_lookup",
                    original_error=str(db_error)
                )

            if not kb:
                raise ResourceNotFoundError(
                    resource_type="Knowledge base",
                    resource_id=f"{kb_id} for tenant {tenant_id}"
                )

            # Generate tenant-specific collection name with error handling
            try:
                qdrant_client = get_qdrant_client()
                tenant_service = get_tenant_service(qdrant_client)
                collection_name = tenant_service.get_collection_name(tenant_id, kb.name)
            except Exception as service_error:
                raise ExternalServiceError(
                    service_name="Qdrant",
                    operation="service_initialization",
                    original_error=str(service_error)
                )
            
            logger.info(
                "Querying collection",
                extra={
                    "collection_name": collection_name,
                    "tenant_id": tenant_id,
                    "kb_name": kb.name
                }
            )

            # Verify collection exists
            try:
                if not tenant_service.collection_exists(collection_name):
                    raise ResourceNotFoundError(
                        resource_type="Qdrant collection",
                        resource_id=collection_name
                    )
            except ResourceNotFoundError:
                raise
            except Exception as collection_error:
                raise ExternalServiceError(
                    service_name="Qdrant",
                    operation="collection_verification",
                    original_error=str(collection_error)
                )

            # Execute RAG query with tracking
            query_start_time = time.time()
            try:
                answer = execute_query(
                    collection_name=collection_name,
                    query=query,
                    chat_history=chat_history or [],
                    tenant_id=tenant_id
                )
            except Exception as query_error:
                raise ExternalServiceError(
                    service_name="RAG Query Engine",
                    operation="query_execution",
                    original_error=str(query_error)
                )
            
            latency_ms = int((time.time() - query_start_time) * 1000)
            
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
                log_error_with_context(
                    logger=logger,
                    message="Failed to track LLM usage",
                    error=track_error,
                    extra_context={"tenant_id": tenant_id, "operation": "rag_query"}
                )

            # Get source documents with error handling
            try:
                retriever = get_retriever(collection_name)
                docs = retriever.invoke(query)
            except Exception as retrieval_error:
                log_error_with_context(
                    logger=logger,
                    message="Failed to retrieve source documents",
                    error=retrieval_error,
                    extra_context={"collection_name": collection_name}
                )
                # Continue without sources rather than failing completely
                docs = []

            # Format sources
            sources = []
            try:
                for i, doc in enumerate(docs[:top_k]):
                    source_info = {
                        "filename": doc.metadata.get("source", "Unknown"),
                        "chunk_number": i + 1,
                        "similarity": doc.metadata.get("score", 0.0),
                        "preview": doc.page_content[:200] if doc.page_content else ""
                    }
                    sources.append(source_info)
            except Exception as source_error:
                log_error_with_context(
                    logger=logger,
                    message="Failed to format source documents",
                    error=source_error
                )
                sources = []

            result = {
                "answer": answer,
                "sources": sources,
                "kb_id": kb_id
            }
            
            # Cache the result (only for queries without chat history)
            if not chat_history:
                try:
                    cache_set(tenant_id, kb_id, query, result, top_k=top_k)
                    logger.debug(
                        "Cached query result",
                        extra={
                            "query_preview": query[:50],
                            "tenant_id": tenant_id,
                            "kb_id": kb_id
                        }
                    )
                except Exception as cache_error:
                    log_error_with_context(
                        logger=logger,
                        message="Failed to cache result",
                        error=cache_error,
                        extra_context={"tenant_id": tenant_id, "kb_id": kb_id}
                    )
            
            duration_ms = int((time.time() - start_time) * 1000)
            log_operation_success(
                logger,
                "query_knowledge_base",
                duration_ms=duration_ms,
                answer_length=len(answer),
                sources_count=len(sources),
                tenant_id=tenant_id
            )
            
            return result

        except (ValidationError, ResourceNotFoundError, DatabaseError, ExternalServiceError):
            # Re-raise known exceptions
            duration_ms = int((time.time() - start_time) * 1000)
            log_operation_failure(
                logger,
                "query_knowledge_base",
                error=e,
                duration_ms=duration_ms,
                tenant_id=tenant_id
            )
            raise
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            log_operation_failure(
                logger,
                "query_knowledge_base",
                error=e,
                duration_ms=duration_ms,
                remediation="Check all service dependencies and database connectivity",
                tenant_id=tenant_id
            )
            
            # Return graceful error response instead of crashing
            return {
                "answer": "I'm sorry, I encountered an unexpected error while processing your question. Please try again in a moment.",
                "sources": [],
                "error": "INTERNAL_ERROR",
                "kb_id": kb_id
            }
        # === END: branch error handling ===

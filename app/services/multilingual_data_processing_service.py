"""
Multilingual Data Processing Service
Parallel implementation of the data processing pipeline with multilingual capabilities
"""

import os
import logging
from typing import List, Dict, Any, Optional

from .extraction_service import extract_data_from_file
from .multilingual_cleaning_service import clean_and_enrich_blocks_with_fallback, get_language_statistics
from .chunking_service import chunk_blocks
from .multilingual_embedding_service import (
    create_embeddings_with_fallback, 
    is_multilingual_enabled,
    get_multilingual_model_info
)
from .qdrant_service import get_qdrant_client, create_collection_if_not_exists, upload_to_qdrant
from .kb_service import add_kb

logger = logging.getLogger(__name__)

# Global service initialization
qdrant_client = get_qdrant_client()

def get_multilingual_collection_name(base_collection_name: str, tenant_id: str = None) -> str:
    """
    Generate multilingual collection name.
    
    Args:
        base_collection_name: Base collection name
        tenant_id: Tenant identifier
        
    Returns:
        Multilingual collection name with _ml suffix
    """
    if is_multilingual_enabled() and tenant_id:
        return f"{base_collection_name}_ml"
    return base_collection_name

async def process_and_upload_file_multilingual(
    file_path: str,
    collection_name: str = "default_collection",
    job_id: str = None,
    tenant_id: str = None,
    force_multilingual: bool = False
):
    """
    Multilingual version of the data processing pipeline.
    
    Orchestrates: Extract -> Clean (Multilingual) -> Chunk -> Embed (BGE-M3) -> Upload
    
    Args:
        file_path: Path to the raw file
        collection_name: Base name of the Qdrant collection
        job_id: Job ID for progress tracking
        tenant_id: Tenant ID for multitenancy isolation
        force_multilingual: Force use of multilingual pipeline
    """
    from .job_service import job_tracker
    
    def update_progress(message: str):
        """Helper to update job progress."""
        print(message)
        if job_id:
            job_tracker.update_progress(job_id, message)
    
    # Determine if multilingual processing should be used
    use_multilingual = force_multilingual or is_multilingual_enabled()
    
    if use_multilingual:
        final_collection_name = get_multilingual_collection_name(collection_name, tenant_id)
        update_progress(f"--- Starting MULTILINGUAL processing pipeline for: {os.path.basename(file_path)} ---")
        update_progress(f"Target collection: {final_collection_name}")
    else:
        final_collection_name = collection_name
        update_progress(f"--- Starting standard processing pipeline for: {os.path.basename(file_path)} ---")
    
    try:
        # 1. Extraction Stage (same as before)
        update_progress("Step 1/6: Starting document extraction...")
        raw_blocks, extraction_metadata = await extract_data_from_file(file_path)
        update_progress(f"Step 1/6: Extraction complete. Found {len(raw_blocks)} blocks.")
        
        # 2. Enhanced Cleaning Stage
        update_progress("Step 2/6: Starting multilingual cleaning and enrichment...")
        enriched_blocks = clean_and_enrich_blocks_with_fallback(raw_blocks, tenant_id)
        
        # Get language statistics
        lang_stats = get_language_statistics(enriched_blocks)
        update_progress(f"Step 2/6: Cleaning complete. {len(enriched_blocks)} blocks remain.")
        update_progress(f"Language distribution: {lang_stats['languages']}")
        
        if lang_stats['multilingual_blocks'] > 0:
            update_progress(f"Found {lang_stats['multilingual_blocks']} multilingual blocks")
        
        # 3. Chunking Stage (same as before)
        update_progress("Step 3/6: Starting text chunking...")
        final_chunks = chunk_blocks(enriched_blocks)
        update_progress(f"Step 3/6: Chunking complete. Generated {len(final_chunks)} chunks.")
        
        # 4. Enhanced Embedding Stage
        if use_multilingual:
            update_progress("Step 4/6: Starting multilingual embedding generation (BGE-M3)...")
            model_info = get_multilingual_model_info()
            update_progress(f"Using model: {model_info['model_name']} (dimension: {model_info['dimension']})")
        else:
            update_progress("Step 4/6: Starting standard embedding generation...")
        
        chunks_with_embeddings = create_embeddings_with_fallback(final_chunks, tenant_id)
        update_progress(f"Step 4/6: Embedding complete. All {len(chunks_with_embeddings)} chunks embedded.")
        
        # 5. Collection Setup
        update_progress("Step 5/6: Setting up vector database collection...")
        
        # Create collection with appropriate configuration
        if use_multilingual:
            # Use BGE-M3 dimension for multilingual collections
            vector_size = get_multilingual_model_info()['dimension']
        else:
            # Use standard dimension for legacy collections
            vector_size = 384  # Default for all-MiniLM-L6-v2
        
        create_collection_if_not_exists(qdrant_client, final_collection_name, vector_size=vector_size)
        add_kb(final_collection_name)
        
        # 6. Upload Stage
        update_progress("Step 6/6: Starting upload to vector database...")
        
        # Add processing metadata to chunks
        processing_metadata = {
            "multilingual_processed": use_multilingual,
            "language_statistics": lang_stats,
            "embedding_model": model_info['model_name'] if use_multilingual else "all-MiniLM-L6-v2",
            "processing_version": "2.0" if use_multilingual else "1.0"
        }
        
        # Attach processing metadata to each chunk
        for chunk in chunks_with_embeddings:
            chunk['metadata'] = chunk.get('metadata', {})
            chunk['metadata'].update(processing_metadata)
        
        upload_to_qdrant(qdrant_client, final_collection_name, chunks_with_embeddings, tenant_id=tenant_id)
        update_progress(f"Step 6/6: Upload complete to collection: {final_collection_name}")
        
        # Final summary
        summary = f"--- Pipeline completed successfully ---"
        summary += f"\nFile: {os.path.basename(file_path)}"
        summary += f"\nCollection: {final_collection_name}"
        summary += f"\nChunks processed: {len(chunks_with_embeddings)}"
        summary += f"\nLanguages detected: {list(lang_stats['languages'].keys())}"
        summary += f"\nMultilingual processing: {'Yes' if use_multilingual else 'No'}"
        
        update_progress(summary)
        
        if job_id:
            job_tracker.complete_job(job_id, {
                "collection_name": final_collection_name,
                "chunks_count": len(chunks_with_embeddings),
                "language_statistics": lang_stats,
                "multilingual_processed": use_multilingual
            })
        
        return {
            "success": True,
            "collection_name": final_collection_name,
            "chunks_count": len(chunks_with_embeddings),
            "language_statistics": lang_stats,
            "multilingual_processed": use_multilingual
        }
            
    except Exception as e:
        error_msg = f"Multilingual processing failed: {str(e)}"
        update_progress(error_msg)
        logger.error(error_msg, exc_info=True)
        
        if job_id:
            job_tracker.fail_job(job_id, error_msg)
        
        raise

async def migrate_collection_to_multilingual(
    source_collection: str,
    target_collection: str = None,
    tenant_id: str = None,
    job_id: str = None
):
    """
    Migrate an existing collection to use multilingual embeddings.
    
    Args:
        source_collection: Name of existing collection
        target_collection: Name of new multilingual collection (optional)
        tenant_id: Tenant identifier
        job_id: Job ID for progress tracking
    """
    from .job_service import job_tracker
    
    def update_progress(message: str):
        """Helper to update job progress."""
        print(message)
        if job_id:
            job_tracker.update_progress(job_id, message)
    
    if not target_collection:
        target_collection = f"{source_collection}_ml"
    
    update_progress(f"--- Starting migration: {source_collection} -> {target_collection} ---")
    
    try:
        # This would involve:
        # 1. Retrieving all documents from source collection
        # 2. Re-processing with multilingual pipeline
        # 3. Uploading to new collection
        # 4. Validation
        
        # For now, just log the intent
        update_progress("Migration functionality to be implemented")
        update_progress("Please re-upload documents to create multilingual collections")
        
        if job_id:
            job_tracker.complete_job(job_id, {
                "message": "Migration placeholder completed",
                "source_collection": source_collection,
                "target_collection": target_collection
            })
        
    except Exception as e:
        error_msg = f"Migration failed: {str(e)}"
        update_progress(error_msg)
        
        if job_id:
            job_tracker.fail_job(job_id, error_msg)
        
        raise

def get_processing_capabilities() -> Dict[str, Any]:
    """
    Get information about current processing capabilities.
    
    Returns:
        Dictionary with capability information
    """
    capabilities = {
        "multilingual_enabled": is_multilingual_enabled(),
        "standard_processing": True,
        "supported_languages": {
            "tier_1": ["en", "es", "fr", "de", "pt"],
            "tier_2": ["it", "nl", "ru", "zh", "ja"],
            "tier_3": "All languages supported by BGE-M3"
        }
    }
    
    if is_multilingual_enabled():
        capabilities["multilingual_model"] = get_multilingual_model_info()
    
    return capabilities

def should_use_multilingual_processing(tenant_id: str = None, file_path: str = None) -> bool:
    """
    Determine if multilingual processing should be used.
    
    Args:
        tenant_id: Tenant identifier
        file_path: Path to file being processed
        
    Returns:
        True if multilingual processing should be used
    """
    # Check if multilingual is enabled globally
    if not is_multilingual_enabled():
        return False
    
    # Add tenant-specific logic here
    # For now, use multilingual for all tenants if enabled
    return True
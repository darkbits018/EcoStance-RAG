from .qdrant_service import get_qdrant_client, delete_collection as delete_qdrant_collection
from .multilingual_integration_service import process_file_intelligently
from .kb_service import get_all_kbs, remove_kb
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def get_all_knowledge_bases():
    """
    Retrieves a list of all knowledge bases from the persistent store.
    """
    return get_all_kbs()

def delete_knowledge_base(collection_name: str):
    """
    Deletes a knowledge base (collection) from Qdrant and the persistent store.
    """
    client = get_qdrant_client()
    if delete_qdrant_collection(client, collection_name):
        remove_kb(collection_name)
        return True
    return False

def delete_points_by_filename(client, collection_name: str, filename: str):
    """
    Deletes all points from a collection that are associated with a specific filename.
    """
    filter_ = Filter(
        must=[
            FieldCondition(
                key="source_filename",  # Corrected key to be top-level
                match=MatchValue(value=filename)
            )
        ]
    )
    client.delete(collection_name=collection_name, points_selector=filter_, wait=True)

def get_knowledge_base_files(collection_name: str) -> List[Dict[str, Any]]:
    """
    Retrieves all files indexed in a specific knowledge base with their metadata.
    """
    client = get_qdrant_client()
    
    try:
        # Get all points from the collection with their payloads
        scroll_result = client.scroll(
            collection_name=collection_name,
            limit=10000,  # Adjust based on your needs
            with_payload=True,
            with_vectors=False  # We don't need vectors for this
        )
        
        points = scroll_result[0]  # First element contains the points
        
        # Group by source filename and collect metadata
        files_info = {}
        
        for point in points:
            payload = point.payload
            source_filename = payload.get('source_filename', 'Unknown')
            
            if source_filename not in files_info:
                # Convert timestamp to readable date
                import datetime
                timestamp = payload.get('ingest_timestamp', 0)
                if timestamp:
                    upload_date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    upload_date = 'Unknown'
                
                # Get language information
                languages = payload.get('language_statistics', {}).get('languages', {})
                language_list = list(languages.keys()) if languages else [payload.get('language', 'unknown')]
                
                files_info[source_filename] = {
                    'filename': source_filename,
                    'chunk_count': 0,
                    'file_type': payload.get('doc_type', 'Unknown'),
                    'upload_date': upload_date,
                    'processing_date': upload_date,
                    'file_size_mb': payload.get('file_size_mb', 'Unknown'),
                    'total_characters': 0,
                    'embedding_model': payload.get('embedding_model', 'Unknown'),
                    'embedding_dimension': payload.get('embedding_dimension', 'Unknown'),
                    'processing_version': payload.get('processing_version', '1.0'),
                    'languages_detected': language_list,
                    'language_count': len(language_list),
                    'multilingual_processed': payload.get('multilingual_processed', False),
                    'extraction_method': payload.get('extraction_method', 'Unknown'),
                    'ocr_confidence': payload.get('ocr_confidence', 1.0),
                    'average_language_confidence': payload.get('language_statistics', {}).get('average_confidence', 0.0),
                    'chunks': []  # Will store sample chunks
                }
            
            # Add chunk information
            chunk_info = {
                'chunk_index': payload.get('chunk_index', files_info[source_filename]['chunk_count']),
                'text_preview': payload.get('text', '')[:200] + '...' if len(payload.get('text', '')) > 200 else payload.get('text', ''),
                'language': payload.get('language', 'unknown'),
                'language_confidence': payload.get('language_confidence', 0.0),
                'page_number': payload.get('page_number', 'Unknown'),
                'text_length': payload.get('text_length', len(payload.get('text', ''))),
                'token_count': payload.get('token_count', 0)
            }
            
            files_info[source_filename]['chunk_count'] += 1
            files_info[source_filename]['total_characters'] += len(payload.get('text', ''))
            
            # Store first 3 chunks as samples
            if len(files_info[source_filename]['chunks']) < 3:
                files_info[source_filename]['chunks'].append(chunk_info)
        
        return list(files_info.values())
        
    except Exception as e:
        logger.error(f"Error retrieving files for collection {collection_name}: {e}")
        return []

def get_knowledge_base_details(collection_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a knowledge base including files and stats.
    """
    client = get_qdrant_client()
    
    try:
        # Get basic collection info without triggering Pydantic validation errors
        # Use scroll to get basic info instead of get_collection
        try:
            # Try to get collection info, but handle Pydantic errors gracefully
            collection_info = client.get_collection(collection_name=collection_name)
            vectors_count = collection_info.points_count
            vector_size = collection_info.config.params.vectors.size
        except Exception as collection_error:
            logger.warning(f"Could not get collection details due to client compatibility issue: {collection_error}")
            # Fallback: use scroll to get basic info
            try:
                scroll_result = client.scroll(
                    collection_name=collection_name,
                    limit=1,
                    with_payload=False,
                    with_vectors=False
                )
                # Get collection from list to get basic info
                collections = client.get_collections()
                collection_exists = any(col.name == collection_name for col in collections.collections)
                if collection_exists:
                    vectors_count = 0  # We'll count from files
                    vector_size = 1024  # Default for BGE-M3, could be improved
                else:
                    raise Exception(f"Collection {collection_name} not found")
            except Exception as fallback_error:
                logger.error(f"Fallback method also failed: {fallback_error}")
                vectors_count = 0
                vector_size = 1024
        
        # Get files information
        files = get_knowledge_base_files(collection_name)
        
        # Calculate aggregate statistics
        total_languages = set()
        total_characters = 0
        embedding_models = set()
        
        for file_info in files:
            total_languages.update(file_info.get('languages_detected', []))
            total_characters += file_info.get('total_characters', 0)
            if file_info.get('embedding_model') != 'Unknown':
                embedding_models.add(file_info.get('embedding_model'))
        
        # If we couldn't get vectors_count from collection info, count from files
        if vectors_count == 0 and files:
            vectors_count = sum(file_info.get('chunk_count', 0) for file_info in files)
        
        return {
            'name': collection_name,
            'vectors_count': vectors_count,
            'vector_size': vector_size,
            'files_count': len(files),
            'files': files,
            'statistics': {
                'total_languages': len(total_languages),
                'languages_list': list(total_languages),
                'total_characters': total_characters,
                'embedding_models': list(embedding_models),
                'distance_metric': 'Cosine'  # Default, since we can't reliably get this due to Pydantic issues
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting details for collection {collection_name}: {e}")
        return {
            'name': collection_name,
            'error': str(e),
            'vectors_count': 0,
            'files_count': 0,
            'files': [],
            'statistics': {}
        }

def get_file_details(collection_name: str, filename: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific file in a knowledge base.
    """
    client = get_qdrant_client()
    
    try:
        # Get all points for this specific file
        from qdrant_client.http.models import Filter, FieldCondition, MatchValue
        
        filter_ = Filter(
            must=[
                FieldCondition(
                    key="source_filename",
                    match=MatchValue(value=filename)
                )
            ]
        )
        
        scroll_result = client.scroll(
            collection_name=collection_name,
            scroll_filter=filter_,
            limit=10000,
            with_payload=True,
            with_vectors=False
        )
        
        points = scroll_result[0]
        
        if not points:
            return {'error': f'File {filename} not found in collection {collection_name}'}
        
        # Aggregate file information from all chunks
        chunks = []
        languages = {}
        total_chars = 0
        pages = set()
        
        # Get metadata from first point (file-level info)
        first_point = points[0].payload
        
        for point in points:
            payload = point.payload
            
            # Collect chunk information
            chunk_info = {
                'id': str(point.id),
                'chunk_index': payload.get('chunk_index', 0),
                'text': payload.get('text', ''),
                'text_length': payload.get('text_length', len(payload.get('text', ''))),
                'language': payload.get('language', 'unknown'),
                'language_confidence': payload.get('language_confidence', 0.0),
                'page_number': payload.get('page_number', 'Unknown'),
                'token_count': payload.get('token_count', 0),
                'is_multilingual': payload.get('is_multilingual', False),
                'languages_detected': payload.get('languages_detected', [])
            }
            chunks.append(chunk_info)
            
            # Aggregate statistics
            lang = payload.get('language', 'unknown')
            languages[lang] = languages.get(lang, 0) + 1
            total_chars += len(payload.get('text', ''))
            if payload.get('page_number') != 'Unknown':
                pages.add(payload.get('page_number'))
        
        # Sort chunks by index
        chunks.sort(key=lambda x: x.get('chunk_index', 0))
        
        # Convert timestamp
        import datetime
        timestamp = first_point.get('ingest_timestamp', 0)
        if timestamp:
            processing_date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        else:
            processing_date = 'Unknown'
        
        return {
            'filename': filename,
            'collection_name': collection_name,
            'file_type': first_point.get('doc_type', 'Unknown'),
            'processing_date': processing_date,
            'file_size_mb': first_point.get('file_size_mb', 'Unknown'),
            'total_chunks': len(chunks),
            'total_characters': total_chars,
            'total_pages': len(pages) if pages else 'Unknown',
            'embedding_model': first_point.get('embedding_model', 'Unknown'),
            'embedding_dimension': first_point.get('embedding_dimension', 'Unknown'),
            'processing_version': first_point.get('processing_version', '1.0'),
            'extraction_method': first_point.get('extraction_method', 'Unknown'),
            'ocr_confidence': first_point.get('ocr_confidence', 1.0),
            'multilingual_processed': first_point.get('multilingual_processed', False),
            'languages': {
                'distribution': languages,
                'total_languages': len(languages),
                'primary_language': max(languages.items(), key=lambda x: x[1])[0] if languages else 'unknown',
                'statistics': first_point.get('language_statistics', {})
            },
            'chunks': chunks
        }
        
    except Exception as e:
        logger.error(f"Error getting file details for {filename} in {collection_name}: {e}")
        return {'error': str(e)}

def delete_file_from_knowledge_base(collection_name: str, filename: str) -> bool:
    """
    Deletes all points associated with a specific file from the knowledge base.
    """
    client = get_qdrant_client()
    
    try:
        delete_points_by_filename(client, collection_name, filename)
        logger.info(f"Successfully deleted file '{filename}' from collection '{collection_name}'")
        return True
    except Exception as e:
        logger.error(f"Error deleting file '{filename}' from collection '{collection_name}': {e}")
        return False

async def reindex_document(file_path: str, collection_name: str, tenant_id: str = None):
    """
    Re-indexes a document by first deleting all its existing points from the
    collection and then running the full processing and upload pipeline again.
    Now uses intelligent processing with multilingual support.
    """
    client = get_qdrant_client()
    
    # First, delete all existing points for this filename.
    delete_points_by_filename(client, collection_name, file_path)
    
    # Now, re-process and upload the file using intelligent processing
    await process_file_intelligently(
        file_path=file_path, 
        collection_name=collection_name,
        tenant_id=tenant_id
    )

def cleanup_stale_kb_references(tenant_id: str, db_session):
    """
    Clean up stale knowledge base references from public chat and agent configs.
    This should be called when configs are loaded to ensure they only reference existing KBs.
    """
    try:
        from app.models.public_chat import PublicChatConfig
        from app.models.public_agent import PublicAgentConfig
        from app.models.tenant_knowledge_base import TenantKnowledgeBase
        import json
        
        # Get all existing KB names for this tenant
        existing_kbs = db_session.query(TenantKnowledgeBase.kb_name).filter(
            TenantKnowledgeBase.tenant_id == tenant_id,
            TenantKnowledgeBase.is_active == True
        ).all()
        existing_kb_names = {kb.kb_name for kb in existing_kbs}
        
        config_updated = False
        
        # Clean up public chat config
        chat_config = db_session.query(PublicChatConfig).filter(
            PublicChatConfig.tenant_id == tenant_id
        ).first()
        
        if chat_config:
            allowed_kbs = json.loads(chat_config.allowed_kbs) if isinstance(chat_config.allowed_kbs, str) else chat_config.allowed_kbs
            original_count = len(allowed_kbs)
            # Keep only KBs that still exist
            allowed_kbs = [kb for kb in allowed_kbs if kb in existing_kb_names]
            
            if len(allowed_kbs) != original_count:
                chat_config.allowed_kbs = json.dumps(allowed_kbs)
                config_updated = True
                logger.info(f"Cleaned up {original_count - len(allowed_kbs)} stale KB references from chat config")
        
        # Clean up public agent config
        agent_config = db_session.query(PublicAgentConfig).filter(
            PublicAgentConfig.tenant_id == tenant_id
        ).first()
        
        if agent_config:
            allowed_kbs = json.loads(agent_config.allowed_kbs) if isinstance(agent_config.allowed_kbs, str) else agent_config.allowed_kbs
            original_count = len(allowed_kbs)
            # Keep only KBs that still exist
            allowed_kbs = [kb for kb in allowed_kbs if kb in existing_kb_names]
            
            if len(allowed_kbs) != original_count:
                agent_config.allowed_kbs = json.dumps(allowed_kbs)
                config_updated = True
                logger.info(f"Cleaned up {original_count - len(allowed_kbs)} stale KB references from agent config")
        
        if config_updated:
            db_session.commit()
            
        return config_updated
        
    except Exception as e:
        logger.error(f"Error cleaning up stale KB references: {e}")
        return False

from .qdrant_service import get_qdrant_client, delete_collection as delete_qdrant_collection
from .data_processing_service import process_and_upload_file
from .kb_service import get_all_kbs, remove_kb
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

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
                key="source_filename",
                match=MatchValue(value=filename)
            )
        ]
    )
    client.delete(collection_name=collection_name, points_selector=filter_)

def reindex_document(file_path: str, collection_name: str):
    """
    Re-indexes a document by first deleting all its existing points from the
    collection and then running the full processing and upload pipeline again.
    """
    client = get_qdrant_client()
    
    # First, delete all existing points for this filename.
    delete_points_by_filename(client, collection_name, file_path)
    
    # Now, re-process and upload the file.
    process_and_upload_file(file_path, collection_name)

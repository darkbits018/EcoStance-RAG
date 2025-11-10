from fastapi import APIRouter, Form, HTTPException, Body
from typing import List

from app.services.management_service import get_all_knowledge_bases, delete_knowledge_base, reindex_document

router = APIRouter()

@router.get("/knowledge-bases/", response_model=List[str])
async def list_knowledge_bases():
    """
    Lists all available knowledge bases (Qdrant collections).
    """
    try:
        return get_all_knowledge_bases()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve knowledge bases: {e}")

@router.delete("/knowledge-bases/{collection_name}")
async def delete_knowledge_base_endpoint(collection_name: str):
    """
    Deletes a specific knowledge base (Qdrant collection).
    """
    try:
        success = delete_knowledge_base(collection_name)
        if success:
            return {"message": f"Knowledge base '{collection_name}' deleted successfully."}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to delete knowledge base '{collection_name}'.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reindex/")
async def reindex_document_endpoint(
    file_path: str = Form(...),
    collection_name: str = Form(...)
):
    """
    Re-indexes a document. This process first deletes all existing data associated
    with the file from the specified collection and then re-runs the full
    ingestion pipeline on the file.
    """
    try:
        reindex_document(file_path, collection_name)
        return {"message": f"Successfully initiated re-indexing for '{file_path}' in collection '{collection_name}'."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to re-index document: {e}")

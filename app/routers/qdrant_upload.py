from fastapi import APIRouter, Form, HTTPException
import os

from ..services.data_processing_service import process_and_upload_file

router = APIRouter()

@router.post("/upload-to-qdrant/")
async def upload_to_qdrant(
    file_path: str = Form(...),
    collection_name: str = Form("default_collection"),
):
    """
    API endpoint to take a path to an already uploaded file, process it 
    through the full pipeline, and upload the results to a specified
    Qdrant collection.
    """
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found at the specified path.")

    try:
        process_and_upload_file(file_path, collection_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed during processing or upload: {e}")

    return {
        "message": f"Successfully processed '{os.path.basename(file_path)}' and uploaded to Qdrant collection '{collection_name}'.",
    }

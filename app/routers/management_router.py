from fastapi import APIRouter, Form, HTTPException, Body, Depends, Request
from typing import List
from pydantic import BaseModel

from app.services.management_service import (
    get_all_knowledge_bases, 
    delete_knowledge_base, 
    reindex_document,
    get_knowledge_base_details,
    get_knowledge_base_files,
    delete_file_from_knowledge_base
)
from app.services.qdrant_service import get_qdrant_client
from app.services.tenant_service import get_tenant_service
from app.auth.dependencies import get_current_user
from app.auth.rbac import RBACService
from app.auth.permissions import Permission
from app.services.audit_service import AuditService
from app.db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

class CreateKBRequest(BaseModel):
    """Request model for creating a knowledge base."""
    kb_name: str


@router.post("/knowledge-bases/")
async def create_knowledge_base(
    kb_request: CreateKBRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new empty knowledge base (Qdrant collection) for the tenant.
    
    Requires: KB_CREATE permission
    """
    kb_name = kb_request.kb_name
    tenant_id = current_user["tenant_id"]
    user_id = current_user["user_id"]
    
    # Check permission
    rbac = RBACService(db)
    rbac.require_permission(tenant_id, user_id, Permission.KB_CREATE)
    
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Generate tenant-specific collection name
        logger.info(f"Creating KB '{kb_name}' for tenant {tenant_id}")
        qdrant_client = get_qdrant_client()
        tenant_service = get_tenant_service(qdrant_client)
        collection_name = tenant_service.get_collection_name(tenant_id, kb_name)
        
        logger.info(f"Collection name: {collection_name}")
        
        # Check if collection already exists
        if tenant_service.collection_exists(collection_name):
            raise HTTPException(
                status_code=409,
                detail=f"Knowledge base '{kb_name}' already exists for this tenant"
            )
        
        # Create the collection
        logger.info(f"Creating collection {collection_name}")
        tenant_service.create_tenant_collection(tenant_id, kb_name)
        logger.info(f"Collection {collection_name} created successfully")
        
        # Log successful creation (non-blocking)
        try:
            audit = AuditService(db)
            audit.log_action(
                tenant_id=tenant_id,
                user_id=user_id,
                action="create_kb",
                resource_type="knowledge_base",
                resource_id=kb_name,
                details={"collection_name": collection_name},
                status="success",
                request=request
            )
        except Exception as audit_error:
            logger.warning(f"Failed to log audit for KB creation: {audit_error}")
            # Don't fail the request if audit logging fails
        
        return {
            "message": f"Knowledge base '{kb_name}' created successfully",
            "kb_name": kb_name,
            "collection_name": collection_name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create KB '{kb_name}': {str(e)}", exc_info=True)
        
        # Log failure
        try:
            audit = AuditService(db)
            audit.log_action(
                tenant_id=tenant_id,
                user_id=user_id,
                action="create_kb",
                resource_type="knowledge_base",
                resource_id=kb_name,
                status="failure",
                error_message=str(e),
                request=request
            )
        except Exception as audit_error:
            logger.error(f"Failed to log audit: {audit_error}")
        
        raise HTTPException(status_code=500, detail=f"Failed to create knowledge base: {str(e)}")


@router.get("/knowledge-bases/", response_model=List[str])
async def list_knowledge_bases(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists all available knowledge bases (Qdrant collections) for the tenant.
    
    Requires: KB_VIEW permission
    """
    tenant_id = current_user["tenant_id"]
    user_id = current_user["user_id"]
    
    # Check permission
    rbac = RBACService(db)
    rbac.require_permission(tenant_id, user_id, Permission.KB_VIEW)
    try:
        # Get all collections and filter for tenant
        all_kbs = get_all_knowledge_bases()
        qdrant_client = get_qdrant_client()
        tenant_service = get_tenant_service(qdrant_client)
        
        # Filter collections that belong to this tenant using proper parsing
        tenant_kbs = []
        for collection_name in all_kbs:
            # Parse collection name to extract tenant_id and kb_name
            parsed = tenant_service.parse_collection_name(collection_name)
            
            # Check if this collection belongs to the current tenant
            if parsed and parsed["tenant_id"] == tenant_service._sanitize_name(tenant_id):
                # Add the KB name (not the full collection name)
                tenant_kbs.append(parsed["kb_name"])
        
        return tenant_kbs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve knowledge bases: {e}")

@router.delete("/knowledge-bases/{kb_name}")
async def delete_knowledge_base_endpoint(
    kb_name: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a specific knowledge base (Qdrant collection) for the tenant.
    
    Requires: KB_DELETE permission
    """
    tenant_id = current_user["tenant_id"]
    user_id = current_user["user_id"]
    
    # Check permission
    rbac = RBACService(db)
    rbac.require_permission(tenant_id, user_id, Permission.KB_DELETE)
    try:
        # Generate tenant-specific collection name
        qdrant_client = get_qdrant_client()
        tenant_service = get_tenant_service(qdrant_client)
        collection_name = tenant_service.get_collection_name(tenant_id, kb_name)
        
        # Verify collection exists
        if not tenant_service.collection_exists(collection_name):
            raise HTTPException(
                status_code=404,
                detail=f"Knowledge base '{kb_name}' not found for tenant"
            )
        
        success = delete_knowledge_base(collection_name)
        if success:
            # Log successful deletion
            audit = AuditService(db)
            audit.log_action(
                tenant_id=tenant_id,
                user_id=user_id,
                action="delete_kb",
                resource_type="knowledge_base",
                resource_id=kb_name,
                details={"collection_name": collection_name},
                status="success",
                request=request
            )
            return {"message": f"Knowledge base '{kb_name}' deleted successfully."}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to delete knowledge base '{kb_name}'.")
    except HTTPException:
        raise
    except Exception as e:
        # Log failure
        audit = AuditService(db)
        audit.log_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action="delete_kb",
            resource_type="knowledge_base",
            resource_id=kb_name,
            status="failure",
            error_message=str(e),
            request=request
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-bases/{kb_name}/details")
async def get_knowledge_base_details_endpoint(
    kb_name: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a knowledge base including all indexed files.
    
    Requires: KB_VIEW permission
    """
    tenant_id = current_user["tenant_id"]
    user_id = current_user["user_id"]
    
    # Check permission
    rbac = RBACService(db)
    rbac.require_permission(tenant_id, user_id, Permission.KB_VIEW)
    try:
        # Generate tenant-specific collection name
        qdrant_client = get_qdrant_client()
        tenant_service = get_tenant_service(qdrant_client)
        collection_name = tenant_service.get_collection_name(tenant_id, kb_name)
        
        # Verify collection exists
        if not tenant_service.collection_exists(collection_name):
            raise HTTPException(
                status_code=404,
                detail=f"Knowledge base '{kb_name}' not found for tenant"
            )
        
        details = get_knowledge_base_details(collection_name)
        # Replace collection name with KB name in response
        details['name'] = kb_name
        details['collection_name'] = collection_name
        return details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge base details: {e}")

@router.get("/knowledge-bases/{kb_name}/files")
async def get_knowledge_base_files_endpoint(
    kb_name: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all files indexed in a specific knowledge base.
    
    Requires: KB_VIEW permission
    """
    tenant_id = current_user["tenant_id"]
    user_id = current_user["user_id"]
    
    # Check permission
    rbac = RBACService(db)
    rbac.require_permission(tenant_id, user_id, Permission.KB_VIEW)
    try:
        # Generate tenant-specific collection name
        qdrant_client = get_qdrant_client()
        tenant_service = get_tenant_service(qdrant_client)
        collection_name = tenant_service.get_collection_name(tenant_id, kb_name)
        
        # Verify collection exists
        if not tenant_service.collection_exists(collection_name):
            raise HTTPException(
                status_code=404,
                detail=f"Knowledge base '{kb_name}' not found for tenant"
            )
        
        files = get_knowledge_base_files(collection_name)
        return {"kb_name": kb_name, "collection_name": collection_name, "files": files}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge base files: {e}")

@router.delete("/knowledge-bases/{kb_name}/files/{filename}")
async def delete_file_endpoint(
    kb_name: str,
    filename: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific file from a knowledge base.
    
    Requires: FILE_DELETE permission
    """
    tenant_id = current_user["tenant_id"]
    user_id = current_user["user_id"]
    
    # Check permission
    rbac = RBACService(db)
    rbac.require_permission(tenant_id, user_id, Permission.FILE_DELETE)
    try:
        # Generate tenant-specific collection name
        qdrant_client = get_qdrant_client()
        tenant_service = get_tenant_service(qdrant_client)
        collection_name = tenant_service.get_collection_name(tenant_id, kb_name)
        
        # Verify collection exists
        if not tenant_service.collection_exists(collection_name):
            raise HTTPException(
                status_code=404,
                detail=f"Knowledge base '{kb_name}' not found for tenant"
            )
        
        success = delete_file_from_knowledge_base(collection_name, filename)
        if success:
            # Log successful deletion
            audit = AuditService(db)
            audit.log_action(
                tenant_id=tenant_id,
                user_id=user_id,
                action="delete_file_from_kb",
                resource_type="file",
                resource_id=filename,
                details={"kb_name": kb_name, "collection_name": collection_name},
                status="success",
                request=request
            )
            return {"message": f"File '{filename}' deleted successfully from '{kb_name}'."}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to delete file '{filename}'.")
    except HTTPException:
        raise
    except Exception as e:
        # Log failure
        audit = AuditService(db)
        audit.log_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action="delete_file_from_kb",
            resource_type="file",
            resource_id=filename,
            details={"kb_name": kb_name},
            status="failure",
            error_message=str(e),
            request=request
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge-bases/{kb_name}/files/{filename}/reindex")
async def reindex_file_endpoint(
    kb_name: str,
    filename: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Re-index a specific file in a knowledge base.
    
    Requires: KB_UPDATE permission
    """
    tenant_id = current_user["tenant_id"]
    user_id = current_user["user_id"]
    
    # Check permission
    rbac = RBACService(db)
    rbac.require_permission(tenant_id, user_id, Permission.KB_UPDATE)
    try:
        # Generate tenant-specific collection name
        qdrant_client = get_qdrant_client()
        tenant_service = get_tenant_service(qdrant_client)
        collection_name = tenant_service.get_collection_name(tenant_id, kb_name)
        
        # Verify collection exists
        if not tenant_service.collection_exists(collection_name):
            raise HTTPException(
                status_code=404,
                detail=f"Knowledge base '{kb_name}' not found for tenant"
            )
        
        reindex_document(filename, collection_name)
        return {"message": f"Successfully initiated re-indexing for '{filename}' in knowledge base '{kb_name}'."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to re-index file: {e}")

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

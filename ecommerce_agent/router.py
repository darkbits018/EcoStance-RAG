"""
Router for E-Commerce Agent
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid

from .service import EcommerceAgentService

router = APIRouter(prefix="/ecomm-agent", tags=["E-Commerce Agent"])
agent_service = EcommerceAgentService()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    
class ChatResponse(BaseModel):
    response: Dict[str, Any] # Structured JSON response
    session_id: str
    success: bool
    error: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    authorization: Optional[str] = Header(None) # Extract Bearer token manually or use Depends(get_current_user)
):
    """
    E-Commerce Chat Endpoint.
    Returns structured JSON: { "type": "...", "message": "...", "data": ... }
    """
    # Simple Mock Auth Extraction for context
    user_id = None
    if authorization and authorization.startswith("Bearer "):
        # In production: decode JWT
        token = authorization.split(" ")[1]
        if token == "valid-mock-token":
            user_id = "user_123"
    
    session_id = request.session_id or str(uuid.uuid4())
    
    result = agent_service.chat(
        session_id=session_id,
        message=request.message,
        user_id=user_id
    )
    
    return result

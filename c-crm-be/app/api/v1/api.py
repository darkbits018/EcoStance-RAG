from fastapi import APIRouter
from app.api.v1.endpoints import auth, dumps, emails, connections

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(connections.router, prefix="/connections", tags=["connections"])
api_router.include_router(dumps.router, prefix="/dumps", tags=["dumps"])
api_router.include_router(emails.router, prefix="/emails", tags=["emails"])


from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings
from contextlib import asynccontextmanager
from app.core.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", lifespan=lifespan)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to Custom CRM Gmail Dump API"}

@app.get("/health")
def health_check():
    """Health check endpoint for Docker and monitoring."""
    return {"status": "healthy"}

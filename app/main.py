from fastapi import FastAPI

from .routers import upload, qdrant_upload, query_router, management_router

app = FastAPI()

app.include_router(upload.router, prefix="/api/v1", tags=["1. File Upload"])
app.include_router(qdrant_upload.router, prefix="/api/v1", tags=["2. Processing & Upload"])
app.include_router(query_router.router, prefix="/api/v1", tags=["3. RAG Query"])
app.include_router(management_router.router, prefix="/api/v1/manage", tags=["4. Management"])


@app.get("/")
def read_root():
    return {"Hello": "World"}

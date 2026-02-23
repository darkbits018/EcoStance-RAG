# Implementation Plan: Hybrid Celery + Shared Embedding Service

This plan outlines the steps to transition the EcoStance RAG pipeline to a hybrid architecture that uses Celery for background processing and a shared internal API for embeddings. This ensures only **one** instance of the BGE-M3 model is loaded in memory.

---

## Phase 1: Environment & Dependencies
1. **Install Redis**:
   - On Windows: Use [Redis-for-Windows](https://github.com/tporadowski/redis/releases) or Memurai.
   - On Linux/Docker: `sudo apt install redis-server`.
2. **Update Python Packages**:
   - Install `celery` and `redis` (python client).
   - Install `httpx` (for internal API calls).

---

## Phase 2: Shared Embedding Engine (The Model Owner)
To prevent RAM duplication across workers, we will create a dedicated "Embedding Server."

1. **Create `app/services/embedding_server.py`**:
   - A lightweight FastAPI application.
   - **Responsibility**: Loads BGE-M3 model into VRAM/RAM.
   - **Endpoint**: `POST /embed` - Accepts text/list of texts, returns vectors.
   - **Port**: Runs on an internal port (e.g., `8001`).

2. **Update `app/services/multilingual_embedding_service.py`**:
   - Refactor to act as a **client**.
   - Instead of using `SentenceTransformer` locally, it will use `httpx` to call `localhost:8001/embed`.
   - **Benefit**: Both the main API (Querying) and the Celery workers (Uploading) will now use this shared engine.

---

## Phase 3: Celery Infrastructure
1. **Create `app/worker/celery_config.py`**:
   - Configure Celery to use Redis as the Broker and Result Backend.
2. **Create `app/worker/tasks.py`**:
   - Define `process_file_task`.
   - Copy logic from `background_process_file` (Extraction -> Cleaning -> Chunking -> Upload).
   - Ensure it uses the persistent `JobTracker` we built to update the database status.

---

## Phase 4: Main API Integration
1. **Update `app/routers/upload.py` and `qdrant_upload.py`**:
   - Remove `BackgroundTasks`.
   - Import `process_file_task`.
   - Replace calling the local function with `process_file_task.delay(...)`.

---

## Phase 5: Execution Workflow
To run the system, you will need to start three separate processes:

1. **The Embedding Server**:
   ```bash
   python app/services/embedding_server.py
   ```
2. **The Celery Worker**:
   ```bash
   celery -A app.worker.tasks worker --loglevel=info -P solo
   ```
3. **The Web API**:
   ```bash
   uvicorn app.main:app --workers 4
   ```

---

## Expected Outcomes
- **RAM Stability**: Exactly **1 copy** of BGE-M3 (2GB) is loaded regardless of how many API workers or Celery workers you have.
- **Instant Response**: FastAPI returns the `job_id` to the UI instantly.
- **Zero Blockage**: The web server never freezes during the "Embedding Stage" because the work is happening in the Celery process.
- **Persistent Status**: Users can refresh their browser and see the real-time progress because the status is saved in the Database.

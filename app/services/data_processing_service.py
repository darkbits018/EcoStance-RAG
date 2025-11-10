from typing import List, Dict, Any
import os

from .extraction_service import extract_data_from_file
from .cleaning_service import clean_and_enrich_blocks
from .chunking_service import chunk_blocks
from .embedding_service import load_embedding_model, create_embeddings
from .qdrant_service import get_qdrant_client, create_collection_if_not_exists, upload_to_qdrant
from .kb_service import add_kb

# --- Global Service Initialization ---
# Load the embedding model and Qdrant client once when the service starts.
# This is crucial for performance, avoiding reconnection on every API call.
embedding_model = load_embedding_model()
qdrant_client = get_qdrant_client()

def process_and_upload_file(file_path: str, collection_name: str = "default_collection"):
    """
    Orchestrates the full data pipeline: Extract -> Clean -> Chunk -> Embed -> Upload.

    Args:
        file_path (str): The path to the raw file.
        collection_name (str): The name of the Qdrant collection to upload to.
    """
    print(f"--- Starting full processing pipeline for file: {os.path.basename(file_path)} ---")
    
    # 1. Extraction Stage
    raw_blocks, _ = extract_data_from_file(file_path)
    print(f"Step 1/5: Extraction complete. Found {len(raw_blocks)} blocks.")

    # 2. Cleaning Stage
    enriched_blocks = clean_and_enrich_blocks(raw_blocks)
    print(f"Step 2/5: Cleaning complete. {len(enriched_blocks)} blocks remain after cleaning.")

    # 3. Chunking Stage
    final_chunks = chunk_blocks(enriched_blocks)
    print(f"Step 3/5: Chunking complete. Generated {len(final_chunks)} chunks.")

    # 4. Embedding Stage
    chunks_with_embeddings = create_embeddings(final_chunks, embedding_model)
    print(f"Step 4/5: Embedding complete. All {len(chunks_with_embeddings)} chunks have been embedded.")

    # 5. Qdrant Upload Stage
    # Ensure the target collection exists before uploading.
    create_collection_if_not_exists(qdrant_client, collection_name)
    add_kb(collection_name)
    # Upload the final, processed data to Qdrant.
    upload_to_qdrant(qdrant_client, collection_name, chunks_with_embeddings)
    print(f"Step 5/5: Upload to Qdrant complete.")
    print(f"--- Pipeline finished for file: {os.path.basename(file_path)} ---")

    # The function now orchestrates the upload but doesn't need to return the data.
    # The API endpoint can return a success message.


import asyncio
import os
import sys
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

# Add project root to path
sys.path.append(os.getcwd())
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

async def search_text():
    print("Connecting to Qdrant...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    collection_name = "tenant_a5ff464b-b13d-45fd-a418-def60ba7d503_test2"
    
    print(f"Scanning '{collection_name}' for 'General Policy'...")
    
    # Scroll through all points and check text content
    offset = None
    found_count = 0
    total_scanned = 0
    
    while True:
        hits, offset = client.scroll(
            collection_name=collection_name,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )
        
        total_scanned += len(hits)
        
        for hit in hits:
            text = hit.payload.get('text', '').lower()
            if "general policy" in text or "hygiene" in text:
                print(f"\n--- MATCH FOUND (ID: {hit.id}) ---")
                print(f"Source: {hit.payload.get('source', 'unknown')}")
                print(f"Text Preview: {hit.payload.get('text', '')[:300]}...")
                found_count += 1
                
        if offset is None:
            break
            
    print(f"\nScanned {total_scanned} points. Found {found_count} matches.")

if __name__ == "__main__":
    asyncio.run(search_text())

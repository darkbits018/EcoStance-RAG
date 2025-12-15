"""
Check knowledge base details to see if audio file is now included
"""
import asyncio
import os
from app.services.qdrant_service import get_qdrant_client

async def check_kb_details():
    """Check the knowledge base details"""
    
    tenant_id = "badcd123-6cc6-4011-b01b-d33d1153f10d"
    kb_name = "test-demo2"
    collection_name = f"tenant_{tenant_id}_{kb_name}"
    
    print(f"🔍 Checking knowledge base: {kb_name}")
    print(f"🗂️ Collection: {collection_name}")
    
    try:
        client = get_qdrant_client()
        
        # Get collection info
        collection_info = client.get_collection(collection_name)
        print(f"📊 Total vectors: {collection_info.vectors_count}")
        
        # Get all points to see files
        scroll_result = client.scroll(
            collection_name=collection_name,
            limit=100,
            with_payload=True
        )
        
        files = {}
        for point in scroll_result[0]:
            payload = point.payload
            filename = payload.get('source_filename', 'unknown')
            file_type = payload.get('doc_type', 'unknown')
            
            if filename not in files:
                files[filename] = {
                    'file_type': file_type,
                    'chunk_count': 0
                }
            files[filename]['chunk_count'] += 1
        
        print(f"\n📁 Files in knowledge base:")
        for filename, info in files.items():
            print(f"  - {filename} ({info['file_type']}) - {info['chunk_count']} chunks")
        
        print(f"\n✅ Total files: {len(files)}")
        print(f"✅ Total chunks: {sum(f['chunk_count'] for f in files.values())}")
        
    except Exception as e:
        print(f"❌ Error checking KB: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_kb_details())
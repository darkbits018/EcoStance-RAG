"""
Reprocess the audio file through the full pipeline
"""
import asyncio
import os
from app.services.data_processing_service import process_and_upload_file

async def reprocess_audio():
    """Reprocess the audio file that failed earlier"""
    
    # Set environment
    os.environ["STT_PROVIDER"] = "whisper_tiny"
    
    # File details from the error log
    audio_file_path = os.path.abspath("uploads/badcd123-6cc6-4011-b01b-d33d1153f10d/call_recording_02.wav")
    tenant_id = "badcd123-6cc6-4011-b01b-d33d1153f10d"
    kb_name = "test-demo2"
    collection_name = f"tenant_{tenant_id}_{kb_name}"
    
    print(f"🔄 Reprocessing audio file: {audio_file_path}")
    print(f"📁 Tenant ID: {tenant_id}")
    print(f"📚 Knowledge Base: {kb_name}")
    print(f"🗂️ Collection: {collection_name}")
    
    try:
        await process_and_upload_file(
            file_path=audio_file_path,
            collection_name=collection_name,
            job_id="manual_reprocess",
            tenant_id=tenant_id
        )
        print("✅ Audio file reprocessed successfully!")
        
    except Exception as e:
        print(f"❌ Reprocessing failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(reprocess_audio())
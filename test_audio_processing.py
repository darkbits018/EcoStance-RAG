"""
Test audio processing with the actual uploaded file
"""
import asyncio
import os
from app.services.extraction_service import extract_data_from_file

async def test_audio_processing():
    """Test audio processing with the uploaded file"""
    
    # Set environment for testing
    os.environ["STT_PROVIDER"] = "whisper_tiny"
    
    audio_file_path = os.path.abspath("uploads/badcd123-6cc6-4011-b01b-d33d1153f10d/call_recording_02.wav")
    
    if not os.path.exists(audio_file_path):
        print(f"❌ Audio file not found: {audio_file_path}")
        return
    
    print(f"🎵 Testing audio processing with: {audio_file_path}")
    print(f"📁 File size: {os.path.getsize(audio_file_path)} bytes")
    
    try:
        # Test the extraction service
        print("🔄 Starting audio extraction...")
        blocks, doc_type = await extract_data_from_file(audio_file_path)
        
        print(f"✅ Audio processing completed!")
        print(f"📊 Document type: {doc_type}")
        print(f"📝 Number of blocks: {len(blocks)}")
        
        if blocks:
            first_block = blocks[0]
            print(f"🎯 First block metadata: {first_block.get('metadata', {})}")
            print(f"📄 Transcribed text preview: {first_block.get('text', '')[:200]}...")
        else:
            print("⚠️ No blocks generated from audio file")
            
    except Exception as e:
        print(f"❌ Audio processing failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_audio_processing())
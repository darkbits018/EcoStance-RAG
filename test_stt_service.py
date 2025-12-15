"""
Test script for STT service
"""
import asyncio
import os
from app.services.stt_service import STTService

async def test_stt_service():
    """Test STT service with different providers"""
    
    # Set environment for testing
    os.environ["STT_PROVIDER"] = "whisper_tiny"
    
    try:
        # Initialize service
        stt_service = STTService()
        print(f"✓ STT Service initialized with provider: {os.getenv('STT_PROVIDER')}")
        
        # Test with a sample audio file (you'll need to provide one)
        # For now, just test the service creation
        print("✓ Service ready for transcription")
        
        # Show available providers
        providers = {
            "whisper_tiny": "Free, fast, good accuracy",
            "whisper_base": "Free, medium speed, better accuracy", 
            "whisper_large": "Free, slow, best accuracy",
            "assemblyai": "Paid, fast, excellent accuracy",
            "azure": "Paid, fast, excellent accuracy",
            "google": "Paid, fast, excellent accuracy"
        }
        
        print("\nAvailable STT Providers:")
        for provider, description in providers.items():
            print(f"  - {provider}: {description}")
        
        print(f"\nCurrent provider: {os.getenv('STT_PROVIDER', 'whisper_tiny')}")
        print("✓ STT service test completed successfully")
        
    except Exception as e:
        print(f"✗ STT service test failed: {str(e)}")
        print("Note: This is expected if Whisper is not installed yet")
        print("Run: pip install openai-whisper")

if __name__ == "__main__":
    asyncio.run(test_stt_service())
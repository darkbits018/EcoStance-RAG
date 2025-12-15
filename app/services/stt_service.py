"""
Speech-to-Text Service with multiple provider support
"""
import os
import tempfile
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class STTProvider(ABC):
    """Abstract base class for STT providers"""
    
    @abstractmethod
    async def transcribe(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Returns:
            {
                "text": "transcribed text",
                "confidence": 0.95,
                "language": "en",
                "provider": "whisper_tiny"
            }
        """
        pass

class WhisperProvider(STTProvider):
    """OpenAI Whisper provider (local processing)"""
    
    def __init__(self, model_size: str = "tiny"):
        self.model_size = model_size
        self.model = None
        
    def _load_model(self):
        """Lazy load Whisper model"""
        if self.model is None:
            try:
                import whisper
                self.model = whisper.load_model(self.model_size)
                logger.info(f"Loaded Whisper model: {self.model_size}")
            except ImportError:
                raise ImportError("whisper package not installed. Run: pip install openai-whisper")
    
    async def transcribe(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe using Whisper"""
        self._load_model()
        
        try:
            # Use librosa to load audio file (works without FFmpeg)
            import librosa
            import numpy as np
            
            # Load audio file using librosa
            audio_data, sample_rate = librosa.load(audio_file_path, sr=16000)
            
            # Convert to numpy array if needed
            if not isinstance(audio_data, np.ndarray):
                audio_data = np.array(audio_data)
            
            # Transcribe using the loaded audio data
            result = self.model.transcribe(audio_data)
            
            return {
                "text": result["text"].strip(),
                "confidence": 0.9,  # Whisper doesn't provide confidence scores
                "language": result.get("language", "unknown"),
                "provider": f"whisper_{self.model_size}"
            }
        except Exception as e:
            logger.error(f"Whisper transcription failed: {str(e)}")
            raise

class AssemblyAIProvider(STTProvider):
    """AssemblyAI cloud provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    async def transcribe(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe using AssemblyAI"""
        try:
            import assemblyai as aai
            aai.settings.api_key = self.api_key
            
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(audio_file_path)
            
            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(f"AssemblyAI error: {transcript.error}")
            
            return {
                "text": transcript.text,
                "confidence": transcript.confidence or 0.9,
                "language": transcript.language_code or "en",
                "provider": "assemblyai"
            }
        except ImportError:
            raise ImportError("assemblyai package not installed. Run: pip install assemblyai")
        except Exception as e:
            logger.error(f"AssemblyAI transcription failed: {str(e)}")
            raise

class AzureSpeechProvider(STTProvider):
    """Azure Speech Services provider"""
    
    def __init__(self, api_key: str, region: str):
        self.api_key = api_key
        self.region = region
        
    async def transcribe(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe using Azure Speech"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            speech_config = speechsdk.SpeechConfig(
                subscription=self.api_key, 
                region=self.region
            )
            audio_input = speechsdk.AudioConfig(filename=audio_file_path)
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, 
                audio_config=audio_input
            )
            
            result = speech_recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return {
                    "text": result.text,
                    "confidence": 0.9,  # Azure doesn't provide detailed confidence
                    "language": speech_config.speech_recognition_language or "en-US",
                    "provider": "azure_speech"
                }
            else:
                raise Exception(f"Azure Speech error: {result.reason}")
                
        except ImportError:
            raise ImportError("azure-cognitiveservices-speech package not installed")
        except Exception as e:
            logger.error(f"Azure Speech transcription failed: {str(e)}")
            raise

class GoogleSpeechProvider(STTProvider):
    """Google Speech-to-Text provider"""
    
    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path
        
    async def transcribe(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe using Google Speech-to-Text"""
        try:
            from google.cloud import speech
            import io
            
            if self.credentials_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path
            
            client = speech.SpeechClient()
            
            with io.open(audio_file_path, "rb") as audio_file:
                content = audio_file.read()
            
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
            )
            
            response = client.recognize(config=config, audio=audio)
            
            if response.results:
                result = response.results[0]
                alternative = result.alternatives[0]
                
                return {
                    "text": alternative.transcript,
                    "confidence": alternative.confidence,
                    "language": config.language_code,
                    "provider": "google_speech"
                }
            else:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "language": "en-US",
                    "provider": "google_speech"
                }
                
        except ImportError:
            raise ImportError("google-cloud-speech package not installed")
        except Exception as e:
            logger.error(f"Google Speech transcription failed: {str(e)}")
            raise

class STTService:
    """Main STT service with provider switching"""
    
    def __init__(self):
        self.provider = self._create_provider()
    
    def _create_provider(self) -> STTProvider:
        """Create STT provider based on environment configuration"""
        provider_name = os.getenv("STT_PROVIDER", "whisper_tiny").lower()
        
        if provider_name.startswith("whisper"):
            model_size = provider_name.replace("whisper_", "") or "tiny"
            return WhisperProvider(model_size)
            
        elif provider_name == "assemblyai":
            api_key = os.getenv("ASSEMBLYAI_API_KEY")
            if not api_key:
                raise ValueError("ASSEMBLYAI_API_KEY environment variable required")
            return AssemblyAIProvider(api_key)
            
        elif provider_name == "azure":
            api_key = os.getenv("AZURE_SPEECH_KEY")
            region = os.getenv("AZURE_SPEECH_REGION")
            if not api_key or not region:
                raise ValueError("AZURE_SPEECH_KEY and AZURE_SPEECH_REGION required")
            return AzureSpeechProvider(api_key, region)
            
        elif provider_name == "google":
            credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
            return GoogleSpeechProvider(credentials_path)
            
        else:
            raise ValueError(f"Unknown STT provider: {provider_name}")
    
    async def transcribe_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Dictionary with transcription results
        """
        try:
            result = await self.provider.transcribe(audio_file_path)
            logger.info(f"Transcription completed using {result['provider']}")
            return result
        except Exception as e:
            logger.error(f"STT transcription failed: {str(e)}")
            raise
    
    async def transcribe_audio_bytes(self, audio_bytes: bytes, filename: str = "audio.wav") -> Dict[str, Any]:
        """
        Transcribe audio from bytes
        
        Args:
            audio_bytes: Audio file bytes
            filename: Original filename (for format detection)
            
        Returns:
            Dictionary with transcription results
        """
        # Save bytes to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        try:
            result = await self.transcribe_audio(temp_file_path)
            return result
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass

# Global STT service instance
stt_service = STTService()
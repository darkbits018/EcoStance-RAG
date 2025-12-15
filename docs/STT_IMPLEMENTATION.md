# Speech-to-Text (STT) Implementation

## Overview
The STT service is integrated into the existing file processing pipeline, allowing audio files to be processed just like any other document type. Users upload audio files through the standard upload endpoints, and the system automatically transcribes them and adds the text to knowledge bases.

## Supported Providers

### Local Providers (Free)
- **Whisper Tiny**: Fast, good accuracy (~80-85%)
- **Whisper Base**: Medium speed, better accuracy (~88-90%)
- **Whisper Large**: Slow, best accuracy (~95%)

### Cloud Providers (Paid)
- **AssemblyAI**: $0.37/hour, excellent accuracy
- **Azure Speech**: $1.00/hour, excellent accuracy
- **Google Speech**: $1.44/hour, excellent accuracy

## Configuration

### Environment Variables
```bash
# Basic Configuration
STT_PROVIDER=whisper_tiny  # Provider to use
WHISPER_MODEL=tiny         # Whisper model size

# AssemblyAI (if using assemblyai provider)
ASSEMBLYAI_API_KEY=your_api_key_here

# Azure Speech (if using azure provider)
AZURE_SPEECH_KEY=your_key_here
AZURE_SPEECH_REGION=eastus

# Google Speech (if using google provider)
GOOGLE_CREDENTIALS_PATH=path/to/credentials.json
```

### Provider Switching
Change the `STT_PROVIDER` environment variable:
- `whisper_tiny` - Fast local processing
- `whisper_base` - Better accuracy local processing
- `whisper_large` - Best accuracy local processing
- `assemblyai` - Cloud processing with AssemblyAI
- `azure` - Cloud processing with Azure Speech
- `google` - Cloud processing with Google Speech-to-Text

## Usage (Integrated with Existing Pipeline)

### Step 1: Upload Audio File
Use the existing upload endpoint:
```http
POST /api/v1/upload/
Content-Type: multipart/form-data

file: meeting_recording.wav
```

**Response:**
```json
{
  "message": "File uploaded successfully. Use the returned path to process the file.",
  "file_path": "uploads/tenant_123/meeting_recording.wav",
  "tenant_id": "tenant_123",
  "filename": "meeting_recording.wav",
  "size_mb": 15.2
}
```

### Step 2: Process Audio to Knowledge Base
Use the existing processing endpoint:
```http
POST /api/v1/upload-to-qdrant/
Content-Type: application/x-www-form-urlencoded

file_path=uploads/tenant_123/meeting_recording.wav
kb_name=meeting_transcripts
```

**Response:**
```json
{
  "message": "Processing started for 'meeting_recording.wav' in knowledge base 'meeting_transcripts'.",
  "job_id": "job_abc123",
  "tenant_id": "tenant_123",
  "kb_name": "meeting_transcripts",
  "status_url": "/api/v1/processing-status/job_abc123"
}
```

### Step 3: Check Processing Status
```http
GET /api/v1/processing-status/job_abc123
```

**Response:**
```json
{
  "job_id": "job_abc123",
  "status": "completed",
  "progress": "Step 5/5: Upload to Qdrant complete.",
  "file_path": "uploads/tenant_123/meeting_recording.wav",
  "collection_name": "tenant_123_meeting_transcripts"
}
```

## Supported Audio Formats
The system automatically detects and processes these audio formats:
- **WAV** (.wav) - Uncompressed audio
- **MP3** (.mp3) - Compressed audio
- **MP4 Audio** (.mp4) - Video container with audio
- **M4A** (.m4a) - Apple audio format
- **AAC** (.aac) - Advanced Audio Coding
- **OGG** (.ogg) - Open source audio format
- **WebM** (.webm) - Web audio format
- **FLAC** (.flac) - Lossless audio compression

## Processing Pipeline
When an audio file is uploaded, it goes through the same pipeline as other documents:

1. **Upload** → Audio file saved to tenant directory
2. **Detection** → System detects audio format
3. **STT Extraction** → Audio transcribed to text using configured provider
4. **Cleaning** → Transcribed text cleaned and enriched
5. **Chunking** → Text split into searchable chunks
6. **Embedding** → Text chunks converted to vector embeddings
7. **Storage** → Embeddings stored in Qdrant with metadata

## Metadata Stored
For audio files, the system stores rich metadata:
```json
{
  "source_filename": "meeting_recording.wav",
  "original_format": "wav",
  "transcription_provider": "whisper_tiny",
  "language": "en",
  "confidence": 0.92,
  "extraction_method": "stt_transcription",
  "content_type": "audio_transcription",
  "doc_type": "wav-transcribed"
}
```

## Search and Retrieval
Once processed, audio transcriptions are searchable just like any other document:
- Users can search for keywords spoken in audio files
- Results show the transcribed text with metadata indicating it came from audio
- Original audio file remains linked for reference

## Installation

### Basic Installation (Whisper only)
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install Whisper
pip install openai-whisper
```

### Optional Cloud Providers
```bash
# AssemblyAI
pip install assemblyai

# Azure Speech
pip install azure-cognitiveservices-speech

# Google Speech-to-Text
pip install google-cloud-speech
```

## Usage Examples

### Development (Fast, Free)
```bash
STT_PROVIDER=whisper_tiny
```

### Production (High Accuracy, Paid)
```bash
STT_PROVIDER=assemblyai
ASSEMBLYAI_API_KEY=your_key_here
```

### High Privacy (Local Processing)
```bash
STT_PROVIDER=whisper_large
```

## Performance Comparison

| Provider | Speed | Accuracy | Cost | Languages |
|----------|-------|----------|------|-----------|
| Whisper Tiny | Fast | Good (80-85%) | Free | 99+ |
| Whisper Base | Medium | Better (88-90%) | Free | 99+ |
| Whisper Large | Slow | Best (95%) | Free | 99+ |
| AssemblyAI | Fast | Excellent (95%) | $0.37/hr | 50+ |
| Azure Speech | Fast | Excellent (95%) | $1.00/hr | 100+ |
| Google Speech | Fast | Excellent (95%) | $1.44/hr | 125+ |

## Error Handling
The service includes comprehensive error handling:
- Invalid audio formats
- Empty files
- Provider-specific errors
- Network issues (for cloud providers)
- API key validation

## Integration Benefits

### Seamless User Experience
- **Same workflow**: Users upload audio files the same way they upload PDFs or Word docs
- **Consistent interface**: No need to learn new endpoints or processes
- **Unified search**: Audio transcriptions appear in search results alongside other documents

### Technical Integration
- **Existing authentication**: Uses your current user/tenant system
- **File management**: Audio files stored in same tenant-specific directories
- **Processing pipeline**: Reuses existing chunking, embedding, and storage logic
- **Error handling**: Benefits from existing error handling and logging
- **Background processing**: Audio transcription happens in background jobs

### File Association
- **Original preservation**: Original audio file is kept for reference/playback
- **Linked content**: Transcribed text is linked to original audio file
- **Version control**: When you implement KB versioning, audio files will be included
- **Metadata rich**: Full metadata about transcription provider, confidence, language

## Testing

### Test STT Service
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Test the service
python test_stt_service.py
```

### Test Full Pipeline
```bash
# 1. Upload audio file
curl -X POST "http://localhost:8000/api/v1/upload/" \
  -H "Authorization: Bearer your_token" \
  -F "file=@test_audio.wav"

# 2. Process to knowledge base
curl -X POST "http://localhost:8000/api/v1/upload-to-qdrant/" \
  -H "Authorization: Bearer your_token" \
  -d "file_path=uploads/tenant_123/test_audio.wav&kb_name=test_kb"

# 3. Check processing status
curl -X GET "http://localhost:8000/api/v1/processing-status/job_id"

# 4. Search transcribed content
curl -X POST "http://localhost:8000/api/v1/query/" \
  -H "Authorization: Bearer your_token" \
  -d "query=keywords from your audio&kb_name=test_kb"
```

## Switching Providers in Production
1. Update `STT_PROVIDER` environment variable
2. Restart the application
3. No code changes required
4. New audio files use new provider
5. Existing transcriptions remain unchanged

## Architecture Benefits
- **Modular design**: STT service is separate but integrated
- **Provider flexibility**: Easy to switch or add new STT providers
- **Backward compatible**: Existing file processing continues to work
- **Future ready**: Easy to extend with features like speaker identification, timestamps, etc.

This implementation provides maximum flexibility while maintaining minimal changes to your existing codebase and preserving the user experience consistency.
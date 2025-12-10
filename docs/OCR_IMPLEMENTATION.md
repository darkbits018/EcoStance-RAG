# OCR Implementation Guide

## Overview

The OCR (Optical Character Recognition) functionality has been implemented to extract text from scanned PDFs and images. The implementation is designed to be **non-disruptive** and **backward-compatible** with the existing system.

## Key Features

✅ **Non-Disruptive**: If OCR fails or is unavailable, the system continues with placeholder text  
✅ **Configurable**: Can be enabled/disabled via environment variables  
✅ **Backward Compatible**: Existing code continues to work without changes  
✅ **Graceful Degradation**: Falls back to placeholder text if OCR is not available  
✅ **Production Ready**: Includes error handling, logging, and monitoring  

## Architecture

### Components

1. **OCR Service** (`app/services/ocr_service.py`)
   - Core OCR functionality
   - Image preprocessing
   - Confidence scoring
   - Error handling

2. **OCR Router** (`app/routers/ocr_router.py`)
   - REST API endpoints
   - Status checking
   - Testing interface

3. **Integration** (`app/services/extraction_service.py`)
   - Seamless integration with existing PDF extraction
   - Automatic fallback for scanned pages

## Installation

### 1. Install Python Dependencies

```bash
# Activate virtual environment
.venv\Scripts\activate

# Install OCR dependencies
pip install pytesseract Pillow pdf2image
```

### 2. Install Tesseract OCR

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (recommended path: `C:\Program Files\Tesseract-OCR`)
3. Add to PATH or set `TESSERACT_CMD` environment variable

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### 3. Configure Environment Variables

Add to your `.env` file:

```env
# OCR Configuration
OCR_ENABLED=true                    # Enable/disable OCR
OCR_LANGUAGE=eng                    # Tesseract language code (eng, fra, deu, etc.)
OCR_MIN_CONFIDENCE=0.3              # Minimum confidence threshold (0.0 to 1.0)
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe  # Windows only, if not in PATH
```

## Usage

### Automatic Usage (PDF Extraction)

OCR is automatically triggered when processing PDFs with scanned pages:

```python
# This happens automatically in the existing upload flow
# No code changes needed!

# When a PDF page has < 50 characters and contains images,
# OCR is automatically triggered
```

### Programmatic Usage (Internal)

```python
from app.services.ocr_service import extract_text_from_image

# Extract text from image bytes
image_bytes = open("scanned_page.png", "rb").read()
text, confidence = extract_text_from_image(image_bytes)

print(f"Extracted: {text}")
print(f"Confidence: {confidence:.2f}")
```

## Configuration Options

### OCR_ENABLED
- **Default**: `true`
- **Values**: `true` / `false`
- **Description**: Master switch for OCR functionality

### OCR_LANGUAGE
- **Default**: `eng`
- **Values**: Tesseract language codes (eng, fra, deu, spa, etc.)
- **Description**: Language for OCR recognition
- **Multiple languages**: `eng+fra` (English + French)

### OCR_MIN_CONFIDENCE
- **Default**: `0.3`
- **Values**: `0.0` to `1.0`
- **Description**: Minimum confidence threshold for accepting OCR results

### TESSERACT_CMD
- **Default**: `None` (uses PATH)
- **Values**: Full path to tesseract executable
- **Description**: Override Tesseract location (Windows only)

## Behavior

### When OCR is Enabled and Available

1. PDF pages with < 50 characters trigger OCR
2. Image is preprocessed (grayscale, contrast, sharpness)
3. Tesseract extracts text with confidence scores
4. If confidence > threshold, text is used
5. If confidence < threshold, low-confidence warning is added

### When OCR is Disabled

- Returns: `"[OCR disabled: enable with OCR_ENABLED=true]"`
- Confidence: `0.0`
- System continues normally

### When OCR is Unavailable

- Returns: `"[OCR unavailable: install pytesseract and Tesseract]"`
- Confidence: `0.0`
- System continues normally

### When OCR Fails

- Returns: `"[OCR error: <error_message>]"`
- Confidence: `0.0`
- Error is logged
- System continues normally

## Testing

### Run OCR Tests

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run OCR-specific tests
python tests/test_ocr_service.py

# Or use pytest
pytest tests/test_ocr_service.py -v
```

### Test Coverage

- ✅ OCR availability check
- ✅ Basic text extraction
- ✅ Image preprocessing
- ✅ Empty/blank images
- ✅ Invalid image data
- ✅ Multi-line text
- ✅ Integration with extraction service

## Monitoring

### Logs

OCR operations are logged with appropriate levels:

- **INFO**: Successful OCR operations
- **WARNING**: Low confidence results, unavailable OCR
- **ERROR**: OCR failures

Check logs in `errorlog.txt` for issues.

## Performance Considerations

### Image Preprocessing

Preprocessing improves accuracy but adds ~100-200ms per page:
- Grayscale conversion
- Contrast enhancement
- Sharpness enhancement

Disable for faster processing:
```python
extract_text_from_image(image_bytes, preprocess=False)
```

### Confidence Thresholds

- **High threshold (0.7+)**: Fewer false positives, may miss valid text
- **Medium threshold (0.3-0.7)**: Balanced approach (recommended)
- **Low threshold (0.0-0.3)**: More text extracted, more errors

## Troubleshooting

### "pytesseract not available"

**Solution**: Install pytesseract
```bash
pip install pytesseract
```

### "Tesseract is not installed"

**Solution**: Install Tesseract OCR binary (see Installation section)

### "TesseractNotFoundError"

**Solution**: Add Tesseract to PATH or set `TESSERACT_CMD`:
```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Low Confidence Results

**Solutions**:
1. Improve image quality (higher resolution, better contrast)
2. Use correct language setting (`OCR_LANGUAGE`)
3. Lower confidence threshold (`OCR_MIN_CONFIDENCE`)
4. Enable preprocessing (default)

### Slow Performance

**Solutions**:
1. Disable preprocessing for simple images
2. Use lower resolution images
3. Consider cloud OCR for production (Google Vision, AWS Textract)

## Migration from Placeholder

The system automatically uses the new OCR implementation. No migration needed!

**Before**: Placeholder text `"[OCR fallback: text would be extracted from image here]"`  
**After**: Real OCR extraction with confidence scores

## Future Enhancements

Potential improvements for future versions:

1. **Cloud OCR Integration**
   - Google Vision AI
   - AWS Textract
   - Azure Computer Vision

2. **Advanced Preprocessing**
   - Deskewing
   - Noise reduction
   - Adaptive thresholding

3. **Multi-Language Support**
   - Auto-detect language
   - Multi-language documents

4. **Background Processing**
   - Async OCR processing
   - Job queue for large documents

5. **Quality Metrics**
   - OCR accuracy tracking
   - Performance monitoring
   - A/B testing different OCR engines

## Support

For issues or questions:
1. Check logs in `errorlog.txt`
2. Run test suite: `python tests/test_ocr_service.py`
3. Review this documentation

## Summary

The OCR implementation is production-ready and designed to enhance the existing system without disruption. It gracefully handles all edge cases and provides clear feedback when OCR is unavailable or fails.

**Key Takeaway**: The system works with or without OCR - it's a feature enhancement, not a requirement.

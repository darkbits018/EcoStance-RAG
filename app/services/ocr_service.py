"""
OCR Service for extracting text from images and scanned PDFs.

This service provides OCR functionality with fallback mechanisms and
configurable options. It's designed to be non-disruptive - if OCR fails,
the system continues with placeholder text.
"""

import io
import os
from typing import Tuple, Optional
from PIL import Image
import logging

logger = logging.getLogger(__name__)

# OCR Configuration
OCR_ENABLED = os.getenv("OCR_ENABLED", "true").lower() == "true"
OCR_LANGUAGE = os.getenv("OCR_LANGUAGE", "eng")  # Tesseract language code
OCR_MIN_CONFIDENCE = float(os.getenv("OCR_MIN_CONFIDENCE", "0.3"))
TESSERACT_CMD = os.getenv("TESSERACT_CMD", None)  # Path to tesseract executable

# Try to import pytesseract, but don't fail if it's not available
try:
    import pytesseract
    if TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    PYTESSERACT_AVAILABLE = True
    logger.info("✓ pytesseract loaded successfully")
except ImportError:
    PYTESSERACT_AVAILABLE = False
    logger.warning("⚠ pytesseract not available. OCR will use placeholder text.")
except Exception as e:
    PYTESSERACT_AVAILABLE = False
    logger.warning(f"⚠ pytesseract initialization failed: {e}")


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess image to improve OCR accuracy.
    
    Args:
        image: PIL Image object
        
    Returns:
        Preprocessed PIL Image object
    """
    try:
        # Convert to grayscale
        image = image.convert('L')
        
        # Increase contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Increase sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        return image
    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}. Using original image.")
        return image


def extract_text_from_image(
    image_bytes: bytes,
    preprocess: bool = True,
    language: Optional[str] = None
) -> Tuple[str, float]:
    """
    Extract text from an image using OCR.
    
    This function is designed to be non-disruptive:
    - If OCR is disabled, returns placeholder text
    - If OCR fails, returns placeholder text with low confidence
    - Never raises exceptions that would break the extraction pipeline
    
    Args:
        image_bytes: Image data as bytes
        preprocess: Whether to preprocess the image for better OCR
        language: Tesseract language code (default: from config)
        
    Returns:
        Tuple of (extracted_text, confidence_score)
        - extracted_text: The OCR'd text or placeholder
        - confidence_score: 0.0 to 1.0, where 1.0 is highest confidence
    """
    # Check if OCR is enabled
    if not OCR_ENABLED:
        logger.debug("OCR is disabled via configuration")
        return "[OCR disabled: enable with OCR_ENABLED=true]", 0.0
    
    # Check if pytesseract is available
    if not PYTESSERACT_AVAILABLE:
        logger.debug("pytesseract not available")
        return "[OCR unavailable: install pytesseract and Tesseract]", 0.0
    
    try:
        # Load image from bytes
        image = Image.open(io.BytesIO(image_bytes))
        
        # Preprocess if requested
        if preprocess:
            image = preprocess_image(image)
        
        # Set language
        lang = language or OCR_LANGUAGE
        
        # Perform OCR with detailed data to get confidence
        ocr_data = pytesseract.image_to_data(
            image,
            lang=lang,
            output_type=pytesseract.Output.DICT
        )
        
        # Extract text and calculate average confidence
        text_parts = []
        confidences = []
        
        for i, conf in enumerate(ocr_data['conf']):
            if conf != -1:  # -1 means no text detected
                text = ocr_data['text'][i].strip()
                if text:
                    text_parts.append(text)
                    confidences.append(float(conf))
        
        # Combine text
        extracted_text = ' '.join(text_parts)
        
        # Calculate average confidence (0-100 from Tesseract, normalize to 0-1)
        if confidences:
            avg_confidence = sum(confidences) / len(confidences) / 100.0
        else:
            avg_confidence = 0.0
        
        # Check if we got meaningful text
        if not extracted_text.strip() or avg_confidence < OCR_MIN_CONFIDENCE:
            logger.warning(
                f"OCR produced low-quality results. "
                f"Text length: {len(extracted_text)}, "
                f"Confidence: {avg_confidence:.2f}"
            )
            return (
                f"[OCR low confidence ({avg_confidence:.2f}): {extracted_text[:100]}...]",
                avg_confidence
            )
        
        logger.info(
            f"✓ OCR successful. Extracted {len(extracted_text)} chars "
            f"with {avg_confidence:.2f} confidence"
        )
        return extracted_text, avg_confidence
        
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}", exc_info=True)
        return f"[OCR error: {str(e)}]", 0.0


def extract_text_from_image_simple(image_bytes: bytes) -> Tuple[str, float]:
    """
    Simplified OCR extraction without preprocessing.
    Useful for quick extraction when image quality is already good.
    
    Args:
        image_bytes: Image data as bytes
        
    Returns:
        Tuple of (extracted_text, confidence_score)
    """
    return extract_text_from_image(image_bytes, preprocess=False)


def check_ocr_availability() -> dict:
    """
    Check OCR system availability and configuration.
    
    Returns:
        Dictionary with OCR status information
    """
    status = {
        "ocr_enabled": OCR_ENABLED,
        "pytesseract_available": PYTESSERACT_AVAILABLE,
        "language": OCR_LANGUAGE,
        "min_confidence": OCR_MIN_CONFIDENCE,
    }
    
    if PYTESSERACT_AVAILABLE:
        try:
            version = pytesseract.get_tesseract_version()
            status["tesseract_version"] = str(version)
            status["status"] = "ready"
        except Exception as e:
            status["status"] = "error"
            status["error"] = str(e)
    else:
        status["status"] = "unavailable"
        status["message"] = "Install pytesseract and Tesseract OCR"
    
    return status


# Backward compatibility: keep the old function signature
def ocr_page_image(page_image: bytes) -> Tuple[str, float]:
    """
    Legacy function name for backward compatibility.
    Calls the new extract_text_from_image function.
    """
    return extract_text_from_image(page_image)

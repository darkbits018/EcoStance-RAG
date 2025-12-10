"""
Tests for OCR service functionality.

These tests verify that the OCR service works correctly and handles
various edge cases gracefully.
"""

import pytest
from PIL import Image, ImageDraw, ImageFont
import io
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ocr_service import (
    extract_text_from_image,
    extract_text_from_image_simple,
    check_ocr_availability,
    preprocess_image,
    OCR_ENABLED,
    PYTESSERACT_AVAILABLE
)


def create_test_image_with_text(text: str, size=(800, 200)) -> bytes:
    """
    Create a test image with text for OCR testing.
    
    Args:
        text: Text to render on the image
        size: Image size (width, height)
        
    Returns:
        Image bytes in PNG format
    """
    # Create a white image
    img = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Draw text in black
    draw.text((50, 80), text, fill='black', font=font)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


class TestOCRService:
    """Test suite for OCR service."""
    
    def test_ocr_availability_check(self):
        """Test that OCR availability check returns valid status."""
        status = check_ocr_availability()
        
        assert isinstance(status, dict)
        assert "ocr_enabled" in status
        assert "pytesseract_available" in status
        assert "status" in status
        
        # Status should be one of: ready, unavailable, error
        assert status["status"] in ["ready", "unavailable", "error"]
    
    def test_extract_text_basic(self):
        """Test basic text extraction from image."""
        # Create test image
        test_text = "Hello World"
        image_bytes = create_test_image_with_text(test_text)
        
        # Extract text
        extracted_text, confidence = extract_text_from_image(image_bytes)
        
        # Verify results
        assert isinstance(extracted_text, str)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
        
        # If OCR is available and enabled, check if text was extracted
        if OCR_ENABLED and PYTESSERACT_AVAILABLE:
            # Text should contain at least part of the original
            assert len(extracted_text) > 0
            print(f"Extracted: '{extracted_text}' (confidence: {confidence:.2f})")
        else:
            # Should return placeholder
            assert "[OCR" in extracted_text or "OCR" in extracted_text
    
    def test_extract_text_simple(self):
        """Test simple extraction without preprocessing."""
        test_text = "Test 123"
        image_bytes = create_test_image_with_text(test_text)
        
        extracted_text, confidence = extract_text_from_image_simple(image_bytes)
        
        assert isinstance(extracted_text, str)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
    
    def test_preprocess_image(self):
        """Test image preprocessing."""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='white')
        
        # Preprocess
        processed = preprocess_image(img)
        
        # Should return an image
        assert isinstance(processed, Image.Image)
        
        # Should be grayscale
        assert processed.mode == 'L'
    
    def test_empty_image(self):
        """Test OCR on empty/blank image."""
        # Create blank white image
        img = Image.new('RGB', (200, 200), color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        
        extracted_text, confidence = extract_text_from_image(img_bytes.getvalue())
        
        # Should handle gracefully
        assert isinstance(extracted_text, str)
        assert isinstance(confidence, float)
        
        # Confidence should be low for blank image
        if OCR_ENABLED and PYTESSERACT_AVAILABLE:
            assert confidence < 0.5
    
    def test_invalid_image_data(self):
        """Test OCR with invalid image data."""
        invalid_data = b"not an image"
        
        extracted_text, confidence = extract_text_from_image(invalid_data)
        
        # Should handle error gracefully
        assert isinstance(extracted_text, str)
        assert isinstance(confidence, float)
        
        # Should indicate error
        if OCR_ENABLED and PYTESSERACT_AVAILABLE:
            assert "error" in extracted_text.lower() or "OCR" in extracted_text
    
    def test_multiple_lines(self):
        """Test OCR with multiple lines of text."""
        # Create image with multiple lines
        img = Image.new('RGB', (800, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "Line 1", fill='black', font=font)
        draw.text((50, 120), "Line 2", fill='black', font=font)
        draw.text((50, 190), "Line 3", fill='black', font=font)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        
        extracted_text, confidence = extract_text_from_image(img_bytes.getvalue())
        
        assert isinstance(extracted_text, str)
        assert isinstance(confidence, float)
        
        if OCR_ENABLED and PYTESSERACT_AVAILABLE:
            print(f"Multi-line extraction: '{extracted_text}'")


def test_ocr_integration_with_extraction_service():
    """Test that OCR integrates properly with extraction service."""
    from app.services.extraction_service import _ocr_page_image
    
    # Create test image
    test_text = "Integration Test"
    image_bytes = create_test_image_with_text(test_text)
    
    # Call the extraction service OCR function
    extracted_text, confidence = _ocr_page_image(image_bytes)
    
    # Should return valid results
    assert isinstance(extracted_text, str)
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0
    
    print(f"Integration test result: '{extracted_text}' (confidence: {confidence:.2f})")


if __name__ == "__main__":
    # Run tests
    print("=" * 60)
    print("OCR Service Test Suite")
    print("=" * 60)
    
    # Check OCR availability
    status = check_ocr_availability()
    print("\nOCR Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Running tests...")
    print("=" * 60 + "\n")
    
    pytest.main([__file__, "-v", "-s"])

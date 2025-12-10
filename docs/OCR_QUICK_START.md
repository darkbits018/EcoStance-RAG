# OCR Quick Start Guide

## ✅ What's Been Implemented

OCR functionality is now fully integrated into your RAG system. It automatically extracts text from scanned PDFs and images.

## 🚀 Quick Setup (3 Steps)

### Step 1: Install Python Dependencies

```bash
# Activate virtual environment
.venv\Scripts\activate

# Install OCR packages
pip install pytesseract Pillow pdf2image
```

### Step 2: Install Tesseract OCR

**Windows:**
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (use default path: `C:\Program Files\Tesseract-OCR`)
3. That's it! (Installer adds to PATH automatically)

**If Tesseract is not in PATH**, add this to your `.env`:
```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Step 3: Verify Installation

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run tests
python tests/test_ocr_service.py
```

## ✨ How It Works

**Automatic**: OCR is triggered automatically when processing PDFs with scanned pages. No code changes needed!

**Safe**: If OCR is unavailable, the system continues with placeholder text. Nothing breaks.

**Configurable**: Control OCR behavior via `.env` file (already configured).

## 🧪 Test OCR

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run the test suite
python tests/test_ocr_service.py
```

## 📋 Configuration (Already Set)

Your `.env` file now includes:
```env
OCR_ENABLED=true              # OCR is enabled
OCR_LANGUAGE=eng              # English language
OCR_MIN_CONFIDENCE=0.3        # Accept results with 30%+ confidence
```

## 🎯 What Happens Now

1. **Upload a scanned PDF** → OCR automatically extracts text
2. **Upload a digital PDF** → Uses normal text extraction (faster)
3. **Mixed PDF** → Uses OCR only for scanned pages

## 🔍 Monitoring

Check logs for OCR activity:
```
✓ OCR successful. Extracted 1234 chars with 0.87 confidence
⚠ OCR low confidence (0.25): [text preview...]
```

## 🛠️ Troubleshooting

**"pytesseract not available"**
```bash
.venv\Scripts\activate
pip install pytesseract Pillow
```

**"Tesseract is not installed"**
- Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki

**"TesseractNotFoundError"**
- Add to `.env`: `TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe`

## 📚 Full Documentation

See `docs/OCR_IMPLEMENTATION.md` for complete details.

## ✅ Summary

- ✅ OCR service created (`app/services/ocr_service.py`)
- ✅ OCR router added (`app/routers/ocr_router.py`)
- ✅ Integrated with PDF extraction (automatic)
- ✅ Tests created (`tests/test_ocr_service.py`)
- ✅ Configuration added to `.env`
- ✅ Documentation complete
- ✅ **Non-disruptive**: System works with or without OCR

**Next Step**: Install Tesseract OCR and run tests!

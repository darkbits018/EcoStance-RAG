"""
Test data management and PDF processing utilities
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import PyPDF2

class MultilingualTestDataManager:
    """Manage test data for multilingual E2E testing."""
    
    def __init__(self, pdf_path: str = "logistics-multilanguage.pdf"):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"Test PDF not found: {pdf_path}")
        
        self.pdf_metadata = None
        self.extracted_text = None
    
    def get_pdf_metadata(self) -> Dict[str, Any]:
        """Extract metadata from test PDF."""
        if self.pdf_metadata:
            return self.pdf_metadata
        
        with open(self.pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            
            self.pdf_metadata = {
                "file_path": str(self.pdf_path),
                "file_size_bytes": self.pdf_path.stat().st_size,
                "file_size_mb": round(self.pdf_path.stat().st_size / (1024 * 1024), 2),
                "num_pages": len(pdf_reader.pages),
                "pdf_version": pdf_reader.pdf_header if hasattr(pdf_reader, 'pdf_header') else None,
                "metadata": pdf_reader.metadata if pdf_reader.metadata else {}
            }
        
        return self.pdf_metadata
    
    def extract_text_from_pdf(self) -> str:
        """Extract all text from test PDF."""
        if self.extracted_text:
            return self.extracted_text
        
        with open(self.pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            
            text_parts = []
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text())
            
            self.extracted_text = "\n".join(text_parts)
        
        return self.extracted_text
    
    def validate_pdf_content(self, expected_keywords: List[str]) -> Dict[str, Any]:
        """Validate that PDF contains expected content."""
        text = self.extract_text_from_pdf()
        text_lower = text.lower()
        
        found_keywords = []
        missing_keywords = []
        
        for keyword in expected_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        return {
            "total_keywords": len(expected_keywords),
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords,
            "coverage_percent": (len(found_keywords) / len(expected_keywords)) * 100,
            "text_length": len(text),
            "validation_passed": len(missing_keywords) == 0
        }
    
    def detect_languages_in_pdf(self) -> Dict[str, Any]:
        """Detect languages present in the PDF (simplified version for testing)."""
        text = self.extract_text_from_pdf()
        
        # Simple heuristic-based language detection for testing
        # This is a simplified version that doesn't require external dependencies
        language_indicators = {
            "en": ["the", "and", "shipping", "delivery", "FAQ", "question"],
            "es": ["el", "la", "y", "envío", "entrega", "preguntas"],
            "fr": ["le", "la", "et", "expédition", "livraison", "questions"],
            "de": ["der", "die", "und", "versand", "lieferung", "fragen"]
        }
        
        text_lower = text.lower()
        detected_languages = {}
        
        for lang, indicators in language_indicators.items():
            count = sum(1 for indicator in indicators if indicator in text_lower)
            if count > 0:
                detected_languages[lang] = {
                    "count": count,
                    "avg_confidence": min(0.9, count * 0.1 + 0.5)  # Simulated confidence
                }
        
        primary_language = max(detected_languages.items(), 
                             key=lambda x: x[1]["count"])[0] if detected_languages else "en"
        
        return {
            "detected_languages": detected_languages,
            "primary_language": primary_language,
            "total_chunks_analyzed": len(text) // 500 + 1
        }
    
    def get_expected_content_samples(self) -> Dict[str, List[str]]:
        """Get expected content samples by language."""
        return {
            "en": [
                "shipping", "delivery", "logistics", "FAQ", "rates", 
                "international", "tracking", "customs", "warehouse"
            ],
            "es": [
                "envío", "entrega", "logística", "preguntas", "tarifas",
                "internacional", "seguimiento", "aduana", "almacén"
            ],
            "fr": [
                "expédition", "livraison", "logistique", "questions", "tarifs",
                "international", "suivi", "douane", "entrepôt"
            ],
            "de": [
                "versand", "lieferung", "logistik", "fragen", "preise",
                "international", "verfolgung", "zoll", "lager"
            ],
            "pt": [
                "envio", "entrega", "logística", "perguntas", "taxas",
                "internacional", "rastreamento", "alfândega", "armazém"
            ]
        }
    
    def generate_multilingual_test_queries(self) -> List[Dict[str, str]]:
        """Generate test queries in multiple languages."""
        return [
            {"language": "en", "query": "What are your shipping rates for international delivery?"},
            {"language": "en", "query": "How long does delivery take?"},
            {"language": "en", "query": "Do you offer pickup services?"},
            
            {"language": "es", "query": "¿Cuáles son sus tarifas de envío para entrega internacional?"},
            {"language": "es", "query": "¿Cuánto tiempo tarda la entrega?"},
            {"language": "es", "query": "¿Ofrecen servicios de recogida?"},
            
            {"language": "fr", "query": "Quels sont vos tarifs d'expédition pour la livraison internationale?"},
            {"language": "fr", "query": "Combien de temps prend la livraison?"},
            {"language": "fr", "query": "Proposez-vous des services de collecte?"},
            
            {"language": "de", "query": "Wie hoch sind Ihre Versandkosten für internationale Lieferungen?"},
            {"language": "de", "query": "Wie lange dauert die Lieferung?"},
            {"language": "de", "query": "Bieten Sie Abholservices an?"},
            
            {"language": "pt", "query": "Quais são suas taxas de envio para entrega internacional?"},
            {"language": "pt", "query": "Quanto tempo leva a entrega?"},
            {"language": "pt", "query": "Vocês oferecem serviços de coleta?"}
        ]
    
    def save_test_results(self, results: Dict[str, Any], output_file: str):
        """Save test results to JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    def load_test_results(self, input_file: str) -> Dict[str, Any]:
        """Load test results from JSON file."""
        with open(input_file, 'r', encoding='utf-8') as f:
            return json.load(f)


class PDFExtractionValidator:
    """Validate PDF extraction results."""
    
    @staticmethod
    def validate_extraction_completeness(original_text: str, extracted_blocks: List[Dict]) -> Dict[str, Any]:
        """Validate that extraction captured all content."""
        extracted_text = " ".join([block.get("text", "") for block in extracted_blocks])
        
        # Calculate coverage
        original_words = set(original_text.lower().split())
        extracted_words = set(extracted_text.lower().split())
        
        common_words = original_words.intersection(extracted_words)
        coverage = (len(common_words) / len(original_words)) * 100 if original_words else 0
        
        return {
            "original_word_count": len(original_words),
            "extracted_word_count": len(extracted_words),
            "common_words": len(common_words),
            "coverage_percent": coverage,
            "total_blocks": len(extracted_blocks),
            "validation_passed": coverage >= 80  # 80% threshold
        }
    
    @staticmethod
    def validate_language_metadata(extracted_blocks: List[Dict]) -> Dict[str, Any]:
        """Validate that language metadata is present."""
        blocks_with_language = 0
        language_distribution = {}
        
        for block in extracted_blocks:
            if "language" in block and block["language"]:
                blocks_with_language += 1
                lang = block["language"]
                language_distribution[lang] = language_distribution.get(lang, 0) + 1
        
        coverage = (blocks_with_language / len(extracted_blocks)) * 100 if extracted_blocks else 0
        
        return {
            "total_blocks": len(extracted_blocks),
            "blocks_with_language": blocks_with_language,
            "language_coverage_percent": coverage,
            "language_distribution": language_distribution,
            "validation_passed": coverage >= 95  # 95% threshold
        }
    
    @staticmethod
    def validate_text_quality(extracted_blocks: List[Dict]) -> Dict[str, Any]:
        """Validate quality of extracted text."""
        issues = []
        empty_blocks = 0
        very_short_blocks = 0
        blocks_with_special_chars = 0
        
        for i, block in enumerate(extracted_blocks):
            text = block.get("text", "")
            
            if not text or not text.strip():
                empty_blocks += 1
                issues.append(f"Block {i}: Empty text")
            elif len(text.strip()) < 10:
                very_short_blocks += 1
            
            # Check for excessive special characters (might indicate extraction issues)
            special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text) if text else 0
            if special_char_ratio > 0.3:
                blocks_with_special_chars += 1
                issues.append(f"Block {i}: High special character ratio ({special_char_ratio:.2%})")
        
        return {
            "total_blocks": len(extracted_blocks),
            "empty_blocks": empty_blocks,
            "very_short_blocks": very_short_blocks,
            "blocks_with_special_chars": blocks_with_special_chars,
            "issues": issues[:10],  # Limit to first 10 issues
            "validation_passed": empty_blocks == 0 and blocks_with_special_chars < len(extracted_blocks) * 0.1
        }
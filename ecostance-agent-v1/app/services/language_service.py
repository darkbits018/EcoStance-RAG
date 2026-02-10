"""
Language Detection and Management Service
Handles language detection, preference storage, and language-aware operations
"""

import logging
from typing import Optional, Dict, List, Tuple
from langdetect import detect, detect_langs, LangDetectException
from functools import lru_cache
import hashlib

# Import multilingual config
from ..config.multilingual_app_config import (
    LANGUAGE_DETECTION_ENABLED,
    LANGUAGE_DETECTION_MIN_CONFIDENCE,
    LANGUAGE_DETECTION_MIN_TEXT_LENGTH,
    TIER_1_LANGUAGES,
    TIER_2_LANGUAGES,
    LOG_LANGUAGE_DETECTION
)

# Constants not in app config but needed
DEFAULT_LANGUAGE = "en"
SESSION_LANGUAGE_MEMORY = True

logger = logging.getLogger(__name__)


class LanguageService:
    """Service for language detection and management."""
    
    def __init__(self):
        self.session_languages: Dict[str, str] = {}  # session_id -> language
        self.user_languages: Dict[str, str] = {}  # user_id -> language
    
    @lru_cache(maxsize=1000)
    def detect_language(self, text: str, return_confidence: bool = False) -> Tuple[str, float] | str:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to detect language from
            return_confidence: If True, return (language, confidence) tuple
            
        Returns:
            Language code (e.g., 'en', 'es') or tuple of (language, confidence)
        """
        if not LANGUAGE_DETECTION_ENABLED:
            return (DEFAULT_LANGUAGE, 1.0) if return_confidence else DEFAULT_LANGUAGE
        
        # Clean and validate text
        text = text.strip()
        
        if len(text) < LANGUAGE_DETECTION_MIN_TEXT_LENGTH:
            if LOG_LANGUAGE_DETECTION:
                logger.debug(f"Text too short for language detection: {len(text)} chars")
            return (DEFAULT_LANGUAGE, 0.5) if return_confidence else DEFAULT_LANGUAGE
        
        try:
            # Get language probabilities
            lang_probs = detect_langs(text)
            
            if not lang_probs:
                return (DEFAULT_LANGUAGE, 0.0) if return_confidence else DEFAULT_LANGUAGE
            
            # Get most probable language
            top_lang = lang_probs[0]
            language = top_lang.lang
            confidence = top_lang.prob
            
            if LOG_LANGUAGE_DETECTION:
                logger.info(f"Detected language: {language} (confidence: {confidence:.2f})")
                if len(lang_probs) > 1:
                    logger.debug(f"Other possibilities: {[(l.lang, l.prob) for l in lang_probs[1:3]]}")
            
            # Check confidence threshold
            if confidence < LANGUAGE_DETECTION_MIN_CONFIDENCE:
                logger.warning(f"Low confidence language detection: {confidence:.2f}, using default")
                return (DEFAULT_LANGUAGE, confidence) if return_confidence else DEFAULT_LANGUAGE
            
            return (language, confidence) if return_confidence else language
            
        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}, using default language")
            return (DEFAULT_LANGUAGE, 0.0) if return_confidence else DEFAULT_LANGUAGE
    
    def detect_languages_batch(self, texts: List[str]) -> List[Tuple[str, float]]:
        """
        Detect languages for multiple texts.
        
        Args:
            texts: List of texts to detect languages from
            
        Returns:
            List of (language, confidence) tuples
        """
        results = []
        for text in texts:
            lang, conf = self.detect_language(text, return_confidence=True)
            results.append((lang, conf))
        return results
    
    def is_multilingual_text(self, text: str, threshold: float = 0.3) -> Tuple[bool, Dict[str, float]]:
        """
        Check if text contains multiple languages.
        
        Args:
            text: Text to analyze
            threshold: Minimum probability for a language to be considered present
            
        Returns:
            Tuple of (is_multilingual, language_distribution)
        """
        try:
            lang_probs = detect_langs(text)
            
            # Build language distribution
            distribution = {lang.lang: lang.prob for lang in lang_probs if lang.prob >= threshold}
            
            is_multilingual = len(distribution) > 1
            
            if LOG_LANGUAGE_DETECTION and is_multilingual:
                logger.info(f"Multilingual text detected: {distribution}")
            
            return is_multilingual, distribution
            
        except LangDetectException:
            return False, {DEFAULT_LANGUAGE: 1.0}
    
    def get_language_tier(self, language: str) -> int:
        """
        Get the support tier for a language.
        
        Args:
            language: Language code
            
        Returns:
            Tier number (1, 2, or 3)
        """
        if language in TIER_1_LANGUAGES:
            return 1
        elif language in TIER_2_LANGUAGES:
            return 2
        else:
            return 3
    
    def set_session_language(self, session_id: str, language: str) -> None:
        """
        Store language preference for a session.
        
        Args:
            session_id: Session identifier
            language: Language code
        """
        if SESSION_LANGUAGE_MEMORY:
            self.session_languages[session_id] = language
            logger.debug(f"Set session {session_id} language to {language}")
    
    def get_session_language(self, session_id: str) -> Optional[str]:
        """
        Get stored language preference for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Language code or None if not set
        """
        return self.session_languages.get(session_id)
    
    def set_user_language(self, user_id: str, language: str) -> None:
        """
        Store language preference for a user.
        
        Args:
            user_id: User identifier
            language: Language code
        """
        self.user_languages[user_id] = language
        logger.debug(f"Set user {user_id} language to {language}")
    
    def get_user_language(self, user_id: str) -> Optional[str]:
        """
        Get stored language preference for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Language code or None if not set
        """
        return self.user_languages.get(user_id)
    
    def get_preferred_language(self, session_id: str = None, user_id: str = None, 
                              detected_language: str = None) -> str:
        """
        Get the preferred language based on session, user, or detected language.
        
        Priority: session > user > detected > default
        
        Args:
            session_id: Optional session identifier
            user_id: Optional user identifier
            detected_language: Optional detected language
            
        Returns:
            Preferred language code
        """
        # Check session preference
        if session_id:
            session_lang = self.get_session_language(session_id)
            if session_lang:
                return session_lang
        
        # Check user preference
        if user_id:
            user_lang = self.get_user_language(user_id)
            if user_lang:
                return user_lang
        
        # Use detected language
        if detected_language:
            return detected_language
        
        # Fall back to default
        return DEFAULT_LANGUAGE
    
    def normalize_language_code(self, language: str) -> str:
        """
        Normalize language code to ISO 639-1 format.
        
        Args:
            language: Language code (may be ISO 639-1 or 639-2)
            
        Returns:
            Normalized language code
        """
        # Map common variations to standard codes
        language_map = {
            'eng': 'en',
            'spa': 'es',
            'fra': 'fr',
            'deu': 'de',
            'por': 'pt',
            'ita': 'it',
            'nld': 'nl',
            'rus': 'ru',
            'zho': 'zh',
            'jpn': 'ja',
        }
        
        language = language.lower()
        return language_map.get(language, language)
    
    def get_language_name(self, language_code: str) -> str:
        """
        Get human-readable language name from code.
        
        Args:
            language_code: ISO 639-1 language code
            
        Returns:
            Language name
        """
        language_names = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'pt': 'Portuguese',
            'it': 'Italian',
            'nl': 'Dutch',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'ko': 'Korean',
        }
        
        return language_names.get(language_code, language_code.upper())
    
    def clear_session_language(self, session_id: str) -> None:
        """Clear language preference for a session."""
        if session_id in self.session_languages:
            del self.session_languages[session_id]
            logger.debug(f"Cleared language preference for session {session_id}")
    
    def get_cache_key(self, text: str) -> str:
        """Generate cache key for language detection."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()


# Global language service instance
_language_service = None

def get_language_service() -> LanguageService:
    """Get or create the global language service instance."""
    global _language_service
    if _language_service is None:
        _language_service = LanguageService()
    return _language_service

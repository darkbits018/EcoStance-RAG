
import logging
from typing import Dict, List, Optional, Tuple
from .language_service import get_language_service

logger = logging.getLogger(__name__)

class MultilingualAgentMixin:
    """Mixin to provide multilingual capabilities to agent services."""
    
    def __init__(self, system_prompts: Dict[str, str], **kwargs):
        self.language_service = get_language_service()
        self.system_prompts = system_prompts
    
    def get_language_context(self, message: str, session_id: str, user_language: Optional[str] = None) -> Tuple[str, str, float]:
        """
        Determine detected language and preferred language.
        
        Returns:
            Tuple of (detected_language, preferred_language, confidence)
        """
        detected_language, confidence = self.language_service.detect_language(
            message, return_confidence=True
        )
        
        preferred_language = self.language_service.get_preferred_language(
            session_id=session_id,
            detected_language=detected_language
        )
        
        if user_language:
            preferred_language = user_language
            
        self.language_service.set_session_language(session_id, preferred_language)
        
        return detected_language, preferred_language, confidence

    def get_system_prompt(self, language: str) -> str:
        """Get system prompt in the appropriate language."""
        # Fallback to English if the specific language prompt isn't found
        return self.system_prompts.get(language, self.system_prompts.get("en", ""))

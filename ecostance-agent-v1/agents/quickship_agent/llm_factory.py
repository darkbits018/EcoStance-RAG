"""
LLM Factory for QuickShip AI Agent
Handles creation of different LLM providers (Gemini, Groq, etc.)
"""

import logging
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from .config import (
    LLM_PROVIDER,
    GOOGLE_API_KEY,
    GROQ_API_KEY,
    AGENT_MODEL,
    AGENT_TEMPERATURE,
    GEMINI_MODELS,
    GROQ_MODELS
)

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory class for creating LLM instances based on provider"""
    
    @staticmethod
    def create_llm(
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ):
        """
        Create an LLM instance based on the specified provider
        
        Args:
            provider: LLM provider ('gemini' or 'groq'). Defaults to LLM_PROVIDER from config
            model: Model name. Defaults to AGENT_MODEL from config
            temperature: Temperature setting. Defaults to AGENT_TEMPERATURE from config
            
        Returns:
            LLM instance (ChatGoogleGenerativeAI or ChatGroq)
            
        Raises:
            ValueError: If provider is not supported or API key is missing
        """
        provider = (provider or LLM_PROVIDER).lower()
        model = model or AGENT_MODEL
        temperature = temperature if temperature is not None else AGENT_TEMPERATURE
        
        logger.info(f"Creating LLM with provider={provider}, model={model}, temperature={temperature}")
        
        if provider == "gemini":
            return LLMFactory._create_gemini_llm(model, temperature)
        elif provider == "groq":
            return LLMFactory._create_groq_llm(model, temperature)
        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported providers: gemini, groq"
            )
    
    @staticmethod
    def _create_gemini_llm(model: str, temperature: float):
        """Create a Google Gemini LLM instance"""
        if not GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )
        
        if model not in GEMINI_MODELS:
            logger.warning(
                f"Model '{model}' not in known Gemini models list. "
                f"Known models: {', '.join(GEMINI_MODELS)}"
            )
        
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=GOOGLE_API_KEY,
            temperature=temperature
        )
    
    @staticmethod
    def _create_groq_llm(model: str, temperature: float):
        """Create a Groq LLM instance"""
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )
        
        if model not in GROQ_MODELS:
            logger.warning(
                f"Model '{model}' not in known Groq models list. "
                f"Known models: {', '.join(GROQ_MODELS)}"
            )
        
        return ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=model,
            temperature=temperature
        )
    
    @staticmethod
    def get_available_providers():
        """Get list of available providers with their API key status"""
        return {
            "gemini": {
                "available": bool(GOOGLE_API_KEY),
                "models": GEMINI_MODELS
            },
            "groq": {
                "available": bool(GROQ_API_KEY),
                "models": GROQ_MODELS
            }
        }
    
    @staticmethod
    def validate_provider_config(provider: str) -> tuple[bool, str]:
        """
        Validate if a provider is properly configured
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        provider = provider.lower()
        
        if provider == "gemini":
            if not GOOGLE_API_KEY:
                return False, "GOOGLE_API_KEY not set in environment"
            return True, ""
        elif provider == "groq":
            if not GROQ_API_KEY:
                return False, "GROQ_API_KEY not set in environment"
            return True, ""
        else:
            return False, f"Unknown provider: {provider}"

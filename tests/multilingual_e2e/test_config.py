"""
Test configuration and environment setup for multilingual E2E testing
"""

import os
import pytest
from pathlib import Path
from typing import Dict, Any

# Test environment configuration
TEST_ENV_CONFIG = {
    "MULTILINGUAL_ENABLED": "true",
    "EMBEDDING_MODEL_TYPE": "bge-m3",
    "LANGUAGE_DETECTION_ENABLED": "true",
    "LANGUAGE_DETECTION_MIN_CONFIDENCE": "0.7",
    "MULTILINGUAL_PROCESSING_ENABLED": "true",
    "AUTO_DETECT_MULTILINGUAL_CONTENT": "true",
    "BGE_M3_BATCH_SIZE": "16",  # Smaller batch for testing
    "BGE_M3_NORMALIZE": "true",
    "MULTILINGUAL_CACHE_ENABLED": "false",  # Disable cache for testing
    "MULTILINGUAL_LOG_LEVEL": "DEBUG"
}

def setup_test_environment():
    """Set up environment variables for testing."""
    for key, value in TEST_ENV_CONFIG.items():
        os.environ[key] = value

def validate_test_environment() -> Dict[str, Any]:
    """Validate that the test environment is properly configured."""
    validation_results = {
        "environment_valid": True,
        "missing_config": [],
        "service_availability": {},
        "file_availability": {}
    }
    
    # Check required environment variables
    required_vars = [
        "MULTILINGUAL_ENABLED",
        "EMBEDDING_MODEL_TYPE",
        "LANGUAGE_DETECTION_ENABLED"
    ]
    
    for var in required_vars:
        if var not in os.environ:
            validation_results["missing_config"].append(var)
            validation_results["environment_valid"] = False
    
    # Check test PDF availability
    pdf_path = Path("logistics-multilanguage.pdf")
    validation_results["file_availability"]["test_pdf"] = pdf_path.exists()
    if not pdf_path.exists():
        validation_results["environment_valid"] = False
    
    # Check service availability
    try:
        from app.config.multilingual_app_config import MULTILINGUAL_ENABLED
        validation_results["service_availability"]["multilingual_config"] = MULTILINGUAL_ENABLED
    except ImportError as e:
        validation_results["service_availability"]["multilingual_config"] = False
        validation_results["environment_valid"] = False
    
    try:
        from app.services.multilingual_integration_service import get_multilingual_integration_service
        service = get_multilingual_integration_service()
        validation_results["service_availability"]["integration_service"] = service.is_available()
    except Exception as e:
        validation_results["service_availability"]["integration_service"] = False
        validation_results["environment_valid"] = False
    
    return validation_results

class TestEnvironmentSetup:
    """Test environment setup and validation."""
    
    @pytest.fixture(autouse=True, scope="session")
    def setup_environment(self):
        """Automatically set up test environment."""
        setup_test_environment()
        
        # Validate environment
        validation = validate_test_environment()
        if not validation["environment_valid"]:
            pytest.fail(f"Test environment validation failed: {validation}")
    
    def test_environment_configuration(self):
        """Test that environment is properly configured."""
        validation = validate_test_environment()
        
        assert validation["environment_valid"], f"Environment validation failed: {validation}"
        assert validation["file_availability"]["test_pdf"], "Test PDF file not found"
        assert validation["service_availability"]["multilingual_config"], "Multilingual config not available"
        assert validation["service_availability"]["integration_service"], "Integration service not available"
    
    def test_multilingual_config_loading(self):
        """Test that multilingual configuration loads correctly."""
        from app.config.multilingual_app_config import (
            MULTILINGUAL_ENABLED,
            BGE_M3_MODEL_NAME,
            BGE_M3_EMBEDDING_DIMENSION,
            TIER_1_LANGUAGES,
            get_multilingual_config_info
        )
        
        assert MULTILINGUAL_ENABLED is True
        assert BGE_M3_MODEL_NAME == "BAAI/bge-m3"
        assert BGE_M3_EMBEDDING_DIMENSION == 1024
        assert "en" in TIER_1_LANGUAGES
        assert "es" in TIER_1_LANGUAGES
        
        config_info = get_multilingual_config_info()
        assert config_info["multilingual_enabled"] is True
        assert config_info["bge_m3_config"]["dimension"] == 1024
    
    def test_integration_service_initialization(self):
        """Test that integration service initializes correctly."""
        from app.services.multilingual_integration_service import get_multilingual_integration_service
        
        service = get_multilingual_integration_service()
        assert service.is_available()
        assert service.initialized
        
        # Test service capabilities
        capabilities = service.get_tenant_capabilities("test_tenant")
        assert capabilities["multilingual_enabled"] is True
        assert capabilities["available_services"]["multilingual_embedding"] is True
        assert capabilities["available_services"]["multilingual_agent"] is True
    
    def test_test_data_availability(self):
        """Test that required test data is available."""
        pdf_path = Path("logistics-multilanguage.pdf")
        assert pdf_path.exists(), "Test PDF file not found"
        assert pdf_path.stat().st_size > 0, "Test PDF file is empty"
        
        # Verify PDF is readable
        with open(pdf_path, 'rb') as f:
            header = f.read(4)
            assert header == b'%PDF', "File is not a valid PDF"
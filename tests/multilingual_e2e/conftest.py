"""
Pytest configuration and fixtures for multilingual E2E testing
"""

import os
import pytest
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

# Test configuration
TEST_TENANT_ID = "test_multilingual_tenant"
TEST_PDF_PATH = "logistics-multilanguage.pdf"
TEST_COLLECTION_SUFFIX = "_ml_test"

# Language configuration
TIER_1_LANGUAGES = ["en", "es", "fr", "de", "pt"]
TIER_2_LANGUAGES = ["it", "nl", "ru", "zh", "ja"]
TEST_LANGUAGES = TIER_1_LANGUAGES + TIER_2_LANGUAGES[:3]  # Focus on key languages

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "document_processing_max_seconds": 30,
    "embedding_generation_min_blocks_per_minute": 100,
    "search_query_max_seconds": 2,
    "agent_response_max_seconds": 5,
    "concurrent_performance_degradation_max_percent": 20
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture."""
    return {
        "tenant_id": TEST_TENANT_ID,
        "pdf_path": TEST_PDF_PATH,
        "collection_suffix": TEST_COLLECTION_SUFFIX,
        "languages": TEST_LANGUAGES,
        "tier_1_languages": TIER_1_LANGUAGES,
        "tier_2_languages": TIER_2_LANGUAGES,
        "performance_thresholds": PERFORMANCE_THRESHOLDS
    }

@pytest.fixture(scope="session")
def test_pdf_path():
    """Path to the test PDF document."""
    pdf_path = Path(TEST_PDF_PATH)
    if not pdf_path.exists():
        pytest.skip(f"Test PDF not found: {TEST_PDF_PATH}")
    return str(pdf_path.absolute())

@pytest.fixture(scope="session")
def multilingual_services():
    """Initialize multilingual services for testing."""
    from app.services.multilingual_integration_service import get_multilingual_integration_service
    
    service = get_multilingual_integration_service()
    if not service.is_available():
        pytest.skip("Multilingual services not available")
    
    return service

@pytest.fixture
def api_client():
    """Mock API test client for testing without full app dependencies."""
    from tests.multilingual_e2e.fixtures.api_client import MockMultilingualAPITestClient
    
    client = MockMultilingualAPITestClient(TEST_TENANT_ID)
    
    yield client
    
    # Cleanup
    client.cleanup()

@pytest.fixture
async def test_session_id():
    """Generate a unique test session ID."""
    import uuid
    return f"test_session_{uuid.uuid4().hex[:8]}"

@pytest.fixture
def language_samples():
    """Sample text in different languages for testing."""
    return {
        "en": "What are your shipping rates for international delivery?",
        "es": "¿Cuáles son sus tarifas de envío para entrega internacional?",
        "fr": "Quels sont vos tarifs d'expédition pour la livraison internationale?",
        "de": "Wie hoch sind Ihre Versandkosten für internationale Lieferungen?",
        "pt": "Quais são suas taxas de envio para entrega internacional?",
        "it": "Quali sono le vostre tariffe di spedizione per la consegna internazionale?",
        "nl": "Wat zijn uw verzendkosten voor internationale levering?",
        "ru": "Каковы ваши тарифы на доставку для международной доставки?",
        "zh": "您的国际配送运费是多少？",
        "ja": "国際配送の送料はいくらですか？"
    }

@pytest.fixture
def expected_content_samples():
    """Expected content samples from the test PDF."""
    return {
        "en": ["shipping", "delivery", "logistics", "FAQ", "rates"],
        "es": ["envío", "entrega", "logística", "preguntas", "tarifas"],
        "fr": ["expédition", "livraison", "logistique", "questions", "tarifs"],
        "de": ["versand", "lieferung", "logistik", "fragen", "preise"]
    }

@pytest.fixture(scope="session")
def cleanup_collections():
    """Fixture to clean up test collections after testing."""
    collections_to_cleanup = []
    
    yield collections_to_cleanup
    
    # Cleanup logic will be implemented in the cleanup utilities
    from tests.multilingual_e2e.utils.cleanup_utils import cleanup_test_collections
    if collections_to_cleanup:
        cleanup_test_collections(collections_to_cleanup)

@pytest.fixture
def property_test_settings():
    """Settings for property-based testing."""
    return {
        "max_examples": 100,  # Minimum 100 iterations per property
        "deadline": 60000,    # 60 seconds timeout per property test
        "suppress_health_check": ["too_slow"]
    }

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "property_test: mark test as property-based test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance benchmark"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "multilingual: mark test as multilingual-specific"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add property_test marker to property-based tests
        if "property_test" in item.name or "test_property" in item.name:
            item.add_marker(pytest.mark.property_test)
        
        # Add performance marker to performance tests
        if "performance" in item.name or "benchmark" in item.name:
            item.add_marker(pytest.mark.performance)
        
        # Add integration marker to integration tests
        if "integration" in item.name or "e2e" in item.name:
            item.add_marker(pytest.mark.integration)
        
        # Add multilingual marker to all tests in this package
        if "multilingual_e2e" in str(item.fspath):
            item.add_marker(pytest.mark.multilingual)
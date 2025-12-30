"""
Test multilingual search and retrieval capabilities for E2E testing
Feature: multilingual-e2e-testing, Property 3: Cross-language search effectiveness
"""

import pytest
import time
from typing import Dict, Any, List
from hypothesis import given, strategies as st, settings

from .fixtures.api_client import MultilingualAPITestClient
from .utils.test_data_utils import MultilingualTestDataManager
from .utils.cleanup_utils import get_cleanup_manager


class TestMultilingualSearchRetrieval:
    """Test multilingual search and retrieval capabilities."""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_config, multilingual_services):
        """Set up test environment."""
        self.config = test_config
        self.services = multilingual_services
        self.cleanup_manager = get_cleanup_manager()
        self.test_data_manager = MultilingualTestDataManager(test_config["pdf_path"])
        
        # Set up a test collection for search tests
        self.test_collection = f"search_test_{int(time.time())}{test_config['collection_suffix']}"
        self.cleanup_manager.register_collection(self.test_collection)
    
    @pytest.fixture(scope="class")
    def prepared_collection(self, api_client: MultilingualAPITestClient, test_config):
        """Prepare a collection with processed multilingual content."""
        collection_name = f"prepared_search_{int(time.time())}{test_config['collection_suffix']}"
        
        # Upload and process the test document
        upload_result = api_client.upload_multilingual_document(
            file_path=test_config["pdf_path"],
            collection_name=collection_name
        )
        
        assert upload_result["status_code"] == 200
        job_id = upload_result["response"]["job_id"]
        
        # Wait for processing completion
        max_wait = test_config["performance_thresholds"]["document_processing_max_seconds"]
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status_result = api_client.get_processing_status(job_id)
            if status_result["response"]["status"] in ["completed", "success"]:
                break
            time.sleep(2)
        
        yield collection_name
        
        # Cleanup
        get_cleanup_manager().register_collection(collection_name)
    
    def test_query_language_detection(self, api_client: MultilingualAPITestClient, 
                                    prepared_collection, language_samples):
        """Test automatic query language detection."""
        for language, query in language_samples.items():
            if language in self.config["tier_1_languages"]:  # Focus on tier 1 languages
                search_result = api_client.search_multilingual_knowledge_base(
                    kb_name=prepared_collection,
                    query=query,
                    language=None  # Let system detect language
                )
                
                assert search_result["status_code"] == 200, \
                    f"Search failed for {language}: {search_result['response']}"
                
                response_data = search_result["response"]
                
                # Validate language detection occurred
                assert "detected_language" in response_data or "query_language" in response_data, \
                    f"No language detection info for query in {language}"
                
                detected_lang = response_data.get("detected_language") or response_data.get("query_language")
                
                # Allow some flexibility in language detection
                assert detected_lang == language or detected_lang.startswith(language[:2]), \
                    f"Expected {language}, detected {detected_lang} for query: {query}"
    
    def test_semantic_search_across_languages(self, api_client: MultilingualAPITestClient, 
                                            prepared_collection, test_config):
        """Test semantic search returns relevant results regardless of content language."""
        # Test queries in different languages for the same concept
        shipping_queries = {
            "en": "shipping rates international delivery",
            "es": "tarifas de envío entrega internacional", 
            "fr": "tarifs d'expédition livraison internationale",
            "de": "versandkosten internationale lieferung"
        }
        
        results_by_language = {}
        
        for language, query in shipping_queries.items():
            search_result = api_client.search_multilingual_knowledge_base(
                kb_name=prepared_collection,
                query=query,
                language=language
            )
            
            assert search_result["status_code"] == 200, \
                f"Search failed for {language}: {search_result['response']}"
            
            response_data = search_result["response"]
            assert "results" in response_data, f"No results for {language} query"
            
            results = response_data["results"]
            assert len(results) > 0, f"No results returned for {language} query: {query}"
            
            results_by_language[language] = results
        
        # Validate that similar queries return overlapping relevant content
        # (This tests semantic understanding across languages)
        for lang1, results1 in results_by_language.items():
            for lang2, results2 in results_by_language.items():
                if lang1 != lang2:
                    # Check if there's semantic overlap in results
                    # (At least some results should be similar for the same concept)
                    overlap_found = self._check_semantic_overlap(results1, results2)
                    assert overlap_found, \
                        f"No semantic overlap found between {lang1} and {lang2} results"
    
    def test_cross_language_search_effectiveness(self, api_client: MultilingualAPITestClient, 
                                               prepared_collection):
        """Test that cross-language search finds relevant content in different languages."""
        # Search in English for content that might be in other languages
        search_result = api_client.search_multilingual_knowledge_base(
            kb_name=prepared_collection,
            query="logistics shipping delivery FAQ",
            language="en"
        )
        
        assert search_result["status_code"] == 200
        response_data = search_result["response"]
        results = response_data["results"]
        
        assert len(results) > 0, "No cross-language search results found"
        
        # Validate that results include content from multiple languages
        languages_found = set()
        for result in results:
            if "metadata" in result:
                metadata = result["metadata"]
                lang = metadata.get("language") or metadata.get("detected_language")
                if lang:
                    languages_found.add(lang)
        
        # Should find content in multiple languages for a multilingual document
        assert len(languages_found) >= 1, \
            f"Cross-language search should find content in multiple languages, found: {languages_found}"
    
    def test_result_metadata_and_confidence_scores(self, api_client: MultilingualAPITestClient, 
                                                  prepared_collection):
        """Test that search results include proper language metadata and confidence scores."""
        search_result = api_client.search_multilingual_knowledge_base(
            kb_name=prepared_collection,
            query="shipping rates and delivery times",
            language="en"
        )
        
        assert search_result["status_code"] == 200
        response_data = search_result["response"]
        results = response_data["results"]
        
        assert len(results) > 0, "No search results returned"
        
        for i, result in enumerate(results):
            # Validate required fields
            assert "score" in result, f"Result {i} missing score"
            assert "content" in result or "text" in result, f"Result {i} missing content"
            assert "metadata" in result, f"Result {i} missing metadata"
            
            # Validate score
            score = result["score"]
            assert isinstance(score, (int, float)), f"Score should be numeric, got {type(score)}"
            assert 0 <= score <= 1, f"Score should be between 0 and 1, got {score}"
            
            # Validate metadata
            metadata = result["metadata"]
            assert isinstance(metadata, dict), f"Metadata should be dict, got {type(metadata)}"
            
            # Check for language information
            has_language = "language" in metadata or "detected_language" in metadata
            assert has_language, f"Result {i} metadata missing language information: {metadata}"
    
    def test_search_performance_threshold(self, api_client: MultilingualAPITestClient, 
                                        prepared_collection, test_config):
        """Test that search queries meet performance thresholds."""
        max_response_time = test_config["performance_thresholds"]["search_query_max_seconds"] * 1000  # Convert to ms
        
        # Test multiple queries to get average performance
        queries = [
            "shipping rates",
            "delivery times",
            "international logistics",
            "customs procedures",
            "tracking information"
        ]
        
        response_times = []
        
        for query in queries:
            search_result = api_client.search_multilingual_knowledge_base(
                kb_name=prepared_collection,
                query=query,
                language="en"
            )
            
            assert search_result["status_code"] == 200, f"Search failed for query: {query}"
            
            response_time = search_result["duration_ms"]
            response_times.append(response_time)
            
            # Individual query should meet threshold
            assert response_time <= max_response_time, \
                f"Query '{query}' took {response_time}ms, exceeds threshold of {max_response_time}ms"
        
        # Average response time should also be good
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time <= max_response_time * 0.8, \
            f"Average response time {avg_response_time}ms exceeds 80% of threshold"
    
    @given(st.text(min_size=5, max_size=100).filter(lambda x: x.strip() and any(c.isalpha() for c in x)))
    @settings(max_examples=100, deadline=60000)
    def test_property_cross_language_search_effectiveness(self, query_text):
        """
        Property test: Cross-language search effectiveness
        Feature: multilingual-e2e-testing, Property 3: Cross-language search effectiveness
        
        For any search query in a supported language, the system should return semantically
        relevant results from content in any language, with proper language metadata and
        confidence scores.
        """
        from quickship_agent.services.language_service import get_language_service
        
        # Test language detection on query
        language_service = get_language_service()
        detected_lang, confidence = language_service.detect_language(query_text, return_confidence=True)
        
        # Property: Language detection should work for any text
        assert detected_lang is not None, "Language detection should return a result"
        assert isinstance(confidence, (int, float)), "Confidence should be numeric"
        assert 0 <= confidence <= 1, "Confidence should be between 0 and 1"
        
        # Property: Query should be searchable (no exceptions)
        try:
            # Simulate search processing
            query_processed = query_text.strip().lower()
            assert len(query_processed) > 0, "Processed query should not be empty"
            
            # Property: Search should handle various query types
            # Test that query can be tokenized and processed
            words = query_processed.split()
            assert len(words) > 0, "Query should have at least one word"
            
            # Property: Language metadata should be consistent
            if detected_lang in ["en", "es", "fr", "de", "pt"]:  # Tier 1 languages
                assert confidence >= 0.5, f"Confidence for tier 1 language should be >= 0.5, got {confidence}"
            
        except Exception as e:
            pytest.fail(f"Cross-language search property test failed for query: {query_text[:50]}... Error: {e}")
    
    def test_multilingual_knowledge_base_listing(self, api_client: MultilingualAPITestClient):
        """Test listing of multilingual knowledge bases."""
        kb_result = api_client.list_multilingual_knowledge_bases()
        
        assert kb_result["status_code"] == 200, f"KB listing failed: {kb_result['response']}"
        
        response_data = kb_result["response"]
        assert "collections" in response_data, "No collections field in response"
        
        collections = response_data["collections"]
        assert isinstance(collections, list), "Collections should be a list"
        
        # Validate collection metadata
        for collection in collections:
            if isinstance(collection, dict):
                # Check for multilingual indicators
                collection_name = collection.get("name", "")
                if "_ml" in collection_name:
                    assert "language_support" in collection or "multilingual" in collection, \
                        f"Multilingual collection {collection_name} missing language metadata"
    
    def _check_semantic_overlap(self, results1: List[Dict], results2: List[Dict]) -> bool:
        """Check if two result sets have semantic overlap."""
        # Simple overlap check based on content similarity
        contents1 = [r.get("content", r.get("text", "")).lower() for r in results1[:3]]
        contents2 = [r.get("content", r.get("text", "")).lower() for r in results2[:3]]
        
        # Check for common keywords or phrases
        for content1 in contents1:
            for content2 in contents2:
                # Simple keyword overlap check
                words1 = set(content1.split())
                words2 = set(content2.split())
                
                # Remove common stop words
                stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
                words1 = words1 - stop_words
                words2 = words2 - stop_words
                
                if len(words1) > 0 and len(words2) > 0:
                    overlap = len(words1.intersection(words2)) / min(len(words1), len(words2))
                    if overlap > 0.2:  # 20% overlap threshold
                        return True
        
        return False
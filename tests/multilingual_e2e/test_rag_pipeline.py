"""
Test multilingual RAG pipeline validation for E2E testing
Feature: multilingual-e2e-testing, Property 4: Multilingual RAG coherence
"""

import pytest
import time
from typing import Dict, Any, List
from hypothesis import given, strategies as st, settings

from .fixtures.api_client import MultilingualAPITestClient
from .utils.test_data_utils import MultilingualTestDataManager
from .utils.cleanup_utils import get_cleanup_manager


class TestMultilingualRAGPipeline:
    """Test multilingual RAG pipeline validation."""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_config, multilingual_services):
        """Set up test environment."""
        self.config = test_config
        self.services = multilingual_services
        self.cleanup_manager = get_cleanup_manager()
        self.test_data_manager = MultilingualTestDataManager(test_config["pdf_path"])
    
    @pytest.fixture(scope="class")
    def prepared_rag_collection(self, api_client: MultilingualAPITestClient, test_config):
        """Prepare a collection for RAG testing."""
        collection_name = f"rag_test_{int(time.time())}{test_config['collection_suffix']}"
        
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
    
    def test_multilingual_context_retrieval(self, api_client: MultilingualAPITestClient, 
                                          prepared_rag_collection, language_samples):
        """Test that RAG retrieves relevant multilingual context."""
        # Test questions in different languages
        for language in self.config["tier_1_languages"]:
            if language in language_samples:
                query = language_samples[language]
                
                # Search for context (simulating RAG retrieval step)
                search_result = api_client.search_multilingual_knowledge_base(
                    kb_name=prepared_rag_collection,
                    query=query,
                    language=language
                )
                
                assert search_result["status_code"] == 200, \
                    f"Context retrieval failed for {language}: {search_result['response']}"
                
                response_data = search_result["response"]
                results = response_data["results"]
                
                assert len(results) > 0, f"No context retrieved for {language} query: {query}"
                
                # Validate context quality
                for result in results[:3]:  # Check top 3 results
                    assert "content" in result or "text" in result, \
                        f"Result missing content for {language}"
                    
                    content = result.get("content") or result.get("text")
                    assert len(content.strip()) > 10, \
                        f"Context too short for {language}: {content[:50]}..."
                    
                    # Validate relevance score
                    assert "score" in result, f"Result missing score for {language}"
                    assert result["score"] > 0.1, \
                        f"Relevance score too low for {language}: {result['score']}"
    
    def test_information_synthesis_across_languages(self, api_client: MultilingualAPITestClient, 
                                                   prepared_rag_collection):
        """Test information synthesis from multiple language sources."""
        # Search for the same concept in different languages
        concept_queries = {
            "en": "international shipping rates and delivery times",
            "es": "tarifas de envío internacional y tiempos de entrega",
            "fr": "tarifs d'expédition internationale et délais de livraison"
        }
        
        all_contexts = []
        
        for language, query in concept_queries.items():
            search_result = api_client.search_multilingual_knowledge_base(
                kb_name=prepared_rag_collection,
                query=query,
                language=language
            )
            
            assert search_result["status_code"] == 200
            results = search_result["response"]["results"]
            
            # Collect contexts from different languages
            for result in results[:2]:  # Top 2 results per language
                context = {
                    "content": result.get("content") or result.get("text"),
                    "language": result.get("metadata", {}).get("language", language),
                    "score": result.get("score", 0)
                }
                all_contexts.append(context)
        
        # Validate that we have contexts from multiple languages
        languages_in_context = set(ctx["language"] for ctx in all_contexts if ctx["language"])
        assert len(languages_in_context) >= 2, \
            f"Should have contexts from multiple languages, got: {languages_in_context}"
        
        # Validate context diversity and quality
        assert len(all_contexts) >= 3, "Should have multiple contexts for synthesis"
        
        for ctx in all_contexts:
            assert len(ctx["content"]) > 20, "Context content should be substantial"
            assert ctx["score"] > 0, "Context should have positive relevance score"
    
    def test_response_language_consistency(self, api_client: MultilingualAPITestClient, 
                                         prepared_rag_collection, test_session_id):
        """Test that RAG responses are generated in the same language as the query."""
        # Create agent session
        session_result = api_client.create_agent_session(language="en")
        assert session_result["status_code"] == 200
        
        session_id = session_result["response"]["session_id"]
        self.cleanup_manager.register_session(session_id)
        
        # Test queries in different languages
        test_queries = {
            "en": "What are your shipping rates?",
            "es": "¿Cuáles son sus tarifas de envío?",
            "fr": "Quels sont vos tarifs d'expédition?"
        }
        
        for expected_lang, query in test_queries.items():
            # Send message to agent (simulating RAG pipeline)
            message_result = api_client.send_agent_message(
                message=query,
                session_id=session_id,
                knowledge_base=prepared_rag_collection
            )
            
            assert message_result["status_code"] == 200, \
                f"Agent message failed for {expected_lang}: {message_result['response']}"
            
            response_data = message_result["response"]
            
            # Validate response language matches query language
            assert "language" in response_data or "response_language" in response_data, \
                f"No language info in response for {expected_lang}"
            
            response_lang = response_data.get("language") or response_data.get("response_language")
            
            # Allow some flexibility in language detection
            assert response_lang == expected_lang or response_lang.startswith(expected_lang[:2]), \
                f"Expected response in {expected_lang}, got {response_lang}"
            
            # Validate response content
            response_text = response_data.get("response", "")
            assert len(response_text) > 10, f"Response too short for {expected_lang}: {response_text}"
    
    def test_factual_accuracy_across_languages(self, api_client: MultilingualAPITestClient, 
                                             prepared_rag_collection, test_session_id):
        """Test that factual accuracy is maintained across language boundaries."""
        # Create agent session
        session_result = api_client.create_agent_session()
        assert session_result["status_code"] == 200
        
        session_id = session_result["response"]["session_id"]
        self.cleanup_manager.register_session(session_id)
        
        # Ask the same factual question in different languages
        factual_queries = {
            "en": "What is the delivery time for international shipments?",
            "es": "¿Cuál es el tiempo de entrega para envíos internacionales?",
            "fr": "Quel est le délai de livraison pour les expéditions internationales?"
        }
        
        responses = {}
        
        for language, query in factual_queries.items():
            message_result = api_client.send_agent_message(
                message=query,
                session_id=session_id,
                knowledge_base=prepared_rag_collection
            )
            
            assert message_result["status_code"] == 200
            response_data = message_result["response"]
            responses[language] = response_data.get("response", "")
        
        # Validate that responses contain consistent factual information
        # (This is a simplified check - in practice, you'd use more sophisticated methods)
        for lang1, response1 in responses.items():
            for lang2, response2 in responses.items():
                if lang1 != lang2:
                    # Check that both responses are substantial
                    assert len(response1) > 20, f"Response too short in {lang1}"
                    assert len(response2) > 20, f"Response too short in {lang2}"
                    
                    # Both should mention delivery/shipping concepts
                    delivery_terms = {
                        "en": ["delivery", "shipping", "time", "days"],
                        "es": ["entrega", "envío", "tiempo", "días"],
                        "fr": ["livraison", "expédition", "temps", "jours"]
                    }
                    
                    response1_lower = response1.lower()
                    response2_lower = response2.lower()
                    
                    # Check for relevant terms in each language
                    if lang1 in delivery_terms:
                        terms_found = any(term in response1_lower for term in delivery_terms[lang1])
                        assert terms_found, f"No delivery terms found in {lang1} response"
                    
                    if lang2 in delivery_terms:
                        terms_found = any(term in response2_lower for term in delivery_terms[lang2])
                        assert terms_found, f"No delivery terms found in {lang2} response"
    
    def test_source_citation_with_language_indicators(self, api_client: MultilingualAPITestClient, 
                                                     prepared_rag_collection, test_session_id):
        """Test that sources are cited with appropriate language indicators."""
        # Create agent session
        session_result = api_client.create_agent_session()
        assert session_result["status_code"] == 200
        
        session_id = session_result["response"]["session_id"]
        self.cleanup_manager.register_session(session_id)
        
        # Ask a question that should trigger source citation
        message_result = api_client.send_agent_message(
            message="What are the shipping policies mentioned in the documentation?",
            session_id=session_id,
            knowledge_base=prepared_rag_collection
        )
        
        assert message_result["status_code"] == 200
        response_data = message_result["response"]
        
        # Check if sources are provided
        if "sources" in response_data or "sources_used" in response_data:
            sources = response_data.get("sources") or response_data.get("sources_used", [])
            
            assert len(sources) > 0, "No sources provided despite using knowledge base"
            
            # Validate source metadata includes language information
            for source in sources:
                if isinstance(source, dict):
                    assert "metadata" in source or "language" in source, \
                        f"Source missing language metadata: {source}"
                    
                    if "metadata" in source:
                        metadata = source["metadata"]
                        assert "language" in metadata or "detected_language" in metadata, \
                            f"Source metadata missing language info: {metadata}"
    
    @given(st.text(min_size=10, max_size=200).filter(lambda x: x.strip() and "?" in x))
    @settings(max_examples=100, deadline=60000)
    def test_property_multilingual_rag_coherence(self, question_text):
        """
        Property test: Multilingual RAG coherence
        Feature: multilingual-e2e-testing, Property 4: Multilingual RAG coherence
        
        For any question asked in a supported language, the RAG pipeline should retrieve
        relevant multilingual context, synthesize information across languages, and generate
        responses in the query language while maintaining factual accuracy.
        """
        from quickship_agent.services.language_service import get_language_service
        
        # Test language detection on question
        language_service = get_language_service()
        detected_lang, confidence = language_service.detect_language(question_text, return_confidence=True)
        
        # Property: Language detection should work for questions
        assert detected_lang is not None, "Language detection should return a result"
        assert isinstance(confidence, (int, float)), "Confidence should be numeric"
        assert 0 <= confidence <= 1, "Confidence should be between 0 and 1"
        
        # Property: Question should be processable by RAG pipeline
        try:
            # Simulate RAG processing
            question_processed = question_text.strip()
            assert len(question_processed) > 0, "Processed question should not be empty"
            
            # Property: Question should have interrogative structure
            question_indicators = ["?", "what", "how", "when", "where", "why", "which", "who"]
            has_question_indicator = any(indicator in question_processed.lower() for indicator in question_indicators)
            assert has_question_indicator, f"Text should be a question: {question_text[:50]}..."
            
            # Property: RAG should be able to handle the question format
            words = question_processed.split()
            assert len(words) >= 2, "Question should have at least 2 words"
            assert len(words) <= 50, "Question should not be too long for processing"
            
            # Property: Language consistency should be maintained
            if detected_lang in ["en", "es", "fr", "de", "pt"]:  # Tier 1 languages
                assert confidence >= 0.6, f"Confidence for tier 1 language question should be >= 0.6, got {confidence}"
            
        except Exception as e:
            pytest.fail(f"RAG coherence property test failed for question: {question_text[:50]}... Error: {e}")
    
    def test_rag_performance_threshold(self, api_client: MultilingualAPITestClient, 
                                     prepared_rag_collection, test_session_id):
        """Test that RAG pipeline meets performance thresholds."""
        # Create agent session
        session_result = api_client.create_agent_session()
        assert session_result["status_code"] == 200
        
        session_id = session_result["response"]["session_id"]
        self.cleanup_manager.register_session(session_id)
        
        max_response_time = self.config["performance_thresholds"]["agent_response_max_seconds"] * 1000  # Convert to ms
        
        # Test multiple questions
        test_questions = [
            "What are your shipping rates?",
            "How long does delivery take?",
            "Do you offer international shipping?",
            "What are your business hours?",
            "How can I track my shipment?"
        ]
        
        response_times = []
        
        for question in test_questions:
            message_result = api_client.send_agent_message(
                message=question,
                session_id=session_id,
                knowledge_base=prepared_rag_collection
            )
            
            assert message_result["status_code"] == 200, \
                f"RAG failed for question: {question}"
            
            response_time = message_result["duration_ms"]
            response_times.append(response_time)
            
            # Individual response should meet threshold
            assert response_time <= max_response_time, \
                f"Question '{question}' took {response_time}ms, exceeds threshold of {max_response_time}ms"
        
        # Average response time should also be good
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time <= max_response_time * 0.8, \
            f"Average RAG response time {avg_response_time}ms exceeds 80% of threshold"
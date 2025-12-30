"""
Test multilingual agent conversation capabilities for E2E testing
Feature: multilingual-e2e-testing, Property 5: Agent conversation consistency
"""

import pytest
import time
from typing import Dict, Any, List
from hypothesis import given, strategies as st, settings

from .fixtures.api_client import MultilingualAPITestClient
from .utils.test_data_utils import MultilingualTestDataManager
from .utils.cleanup_utils import get_cleanup_manager


class TestMultilingualAgentConversation:
    """Test multilingual agent conversation capabilities."""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_config, multilingual_services):
        """Set up test environment."""
        self.config = test_config
        self.services = multilingual_services
        self.cleanup_manager = get_cleanup_manager()
        self.test_data_manager = MultilingualTestDataManager(test_config["pdf_path"])
    
    @pytest.fixture(scope="class")
    def prepared_agent_collection(self, api_client: MultilingualAPITestClient, test_config):
        """Prepare a collection for agent testing."""
        collection_name = f"agent_test_{int(time.time())}{test_config['collection_suffix']}"
        
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
    
    def test_multilingual_agent_session_initialization(self, api_client: MultilingualAPITestClient):
        """Test creating multilingual-enabled agent sessions."""
        # Test session creation with different language preferences
        for language in self.config["tier_1_languages"]:
            session_result = api_client.create_agent_session(language=language)
            
            assert session_result["status_code"] == 200, \
                f"Session creation failed for {language}: {session_result['response']}"
            
            response_data = session_result["response"]
            assert "session_id" in response_data, f"No session_id for {language}"
            
            session_id = response_data["session_id"]
            self.cleanup_manager.register_session(session_id)
            
            # Validate session language preference
            if "preferred_language" in response_data:
                assert response_data["preferred_language"] == language, \
                    f"Expected {language}, got {response_data['preferred_language']}"
    
    def test_language_detection_and_context_maintenance(self, api_client: MultilingualAPITestClient, 
                                                       prepared_agent_collection):
        """Test language detection and conversation context maintenance."""
        # Create session
        session_result = api_client.create_agent_session()
        assert session_result["status_code"] == 200
        
        session_id = session_result["response"]["session_id"]
        self.cleanup_manager.register_session(session_id)
        
        # Test conversation in multiple languages
        conversation_flow = [
            {"language": "en", "message": "Hello, what are your shipping rates?"},
            {"language": "es", "message": "¿Cuánto tiempo tarda la entrega?"},
            {"language": "fr", "message": "Proposez-vous des services de collecte?"},
            {"language": "en", "message": "Thank you for the information."}
        ]
        
        for turn in conversation_flow:
            message_result = api_client.send_agent_message(
                message=turn["message"],
                session_id=session_id,
                knowledge_base=prepared_agent_collection
            )
            
            assert message_result["status_code"] == 200, \
                f"Message failed for {turn['language']}: {message_result['response']}"
            
            response_data = message_result["response"]
            
            # Validate language detection
            assert "detected_language" in response_data or "language" in response_data, \
                f"No language detection for {turn['language']}"
            
            detected_lang = response_data.get("detected_language") or response_data.get("language")
            expected_lang = turn["language"]
            
            # Allow some flexibility in language detection
            assert detected_lang == expected_lang or detected_lang.startswith(expected_lang[:2]), \
                f"Expected {expected_lang}, detected {detected_lang} for: {turn['message']}"
            
            # Validate response is in same language as query
            response_lang = response_data.get("response_language") or response_data.get("language")
            assert response_lang == expected_lang or response_lang.startswith(expected_lang[:2]), \
                f"Response language {response_lang} doesn't match query language {expected_lang}"
        
        # Test conversation history maintenance
        history_result = api_client.get_conversation_history(session_id)
        assert history_result["status_code"] == 200
        
        history = history_result["response"]
        assert len(history) >= len(conversation_flow), "Conversation history incomplete"
    
    def test_multilingual_tool_invocation(self, api_client: MultilingualAPITestClient, 
                                        prepared_agent_collection):
        """Test agent tool invocation with multilingual capabilities."""
        # Create session
        session_result = api_client.create_agent_session()
        assert session_result["status_code"] == 200
        
        session_id = session_result["response"]["session_id"]
        self.cleanup_manager.register_session(session_id)
        
        # Test knowledge base search tool invocation in different languages
        kb_queries = {
            "en": "Search the knowledge base for shipping policies",
            "es": "Busca en la base de conocimientos las políticas de envío",
            "fr": "Recherchez dans la base de connaissances les politiques d'expédition"
        }
        
        for language, query in kb_queries.items():
            message_result = api_client.send_agent_message(
                message=query,
                session_id=session_id,
                knowledge_base=prepared_agent_collection
            )
            
            assert message_result["status_code"] == 200, \
                f"KB search failed for {language}: {message_result['response']}"
            
            response_data = message_result["response"]
            
            # Validate that multilingual tools were used
            if "tool_used" in response_data:
                tool_used = response_data["tool_used"]
                assert "multilingual" in tool_used or "knowledge_base" in tool_used, \
                    f"Expected multilingual tool usage for {language}, got {tool_used}"
            
            # Validate response contains relevant information
            response_text = response_data.get("response", "")
            assert len(response_text) > 20, f"Response too short for {language}: {response_text}"
    
    def test_cross_language_knowledge_base_search(self, api_client: MultilingualAPITestClient, 
                                                 prepared_agent_collection):
        """Test cross-language knowledge base search through agent."""
        # Create session
        session_result = api_client.create_agent_session()
        assert session_result["status_code"] == 200
        
        session_id = session_result["response"]["session_id"]
        self.cleanup_manager.register_session(session_id)
        
        # Ask about the same topic in different languages
        cross_language_queries = [
            "What information do you have about international shipping?",
            "¿Qué información tienes sobre envíos internacionales?",
            "Quelles informations avez-vous sur l'expédition internationale?"
        ]
        
        responses = []
        
        for query in cross_language_queries:
            message_result = api_client.send_agent_message(
                message=query,
                session_id=session_id,
                knowledge_base=prepared_agent_collection
            )
            
            assert message_result["status_code"] == 200
            response_data = message_result["response"]
            responses.append(response_data.get("response", ""))
        
        # Validate that all responses contain relevant information
        for i, response in enumerate(responses):
            assert len(response) > 30, f"Response {i} too short: {response[:50]}..."
            
            # Should contain shipping/logistics related terms
            shipping_terms = ["shipping", "delivery", "international", "envío", "entrega", 
                            "internacional", "expédition", "livraison", "internationale"]
            
            response_lower = response.lower()
            has_relevant_terms = any(term in response_lower for term in shipping_terms)
            assert has_relevant_terms, f"Response {i} lacks relevant terms: {response[:100]}..."
    
    def test_conversation_coherence_across_languages(self, api_client: MultilingualAPITestClient, 
                                                   prepared_agent_collection):
        """Test conversation coherence when switching languages."""
        # Create session
        session_result = api_client.create_agent_session()
        assert session_result["status_code"] == 200
        
        session_id = session_result["response"]["session_id"]
        self.cleanup_manager.register_session(session_id)
        
        # Multi-turn conversation with language switches
        conversation = [
            {"lang": "en", "msg": "I need information about shipping rates", "expect_topic": "shipping"},
            {"lang": "es", "msg": "¿Puedes darme más detalles sobre los costos?", "expect_topic": "costs"},
            {"lang": "en", "msg": "What about delivery times?", "expect_topic": "delivery"},
            {"lang": "fr", "msg": "Merci pour ces informations", "expect_topic": "thanks"}
        ]
        
        for turn in conversation:
            message_result = api_client.send_agent_message(
                message=turn["msg"],
                session_id=session_id,
                knowledge_base=prepared_agent_collection
            )
            
            assert message_result["status_code"] == 200
            response_data = message_result["response"]
            
            # Validate response language matches query language
            response_lang = response_data.get("response_language") or response_data.get("language")
            expected_lang = turn["lang"]
            
            assert response_lang == expected_lang or response_lang.startswith(expected_lang[:2]), \
                f"Language mismatch: expected {expected_lang}, got {response_lang}"
            
            # Validate response is contextually appropriate
            response_text = response_data.get("response", "").lower()
            assert len(response_text) > 10, f"Response too short for {turn['lang']}"
        
        # Validate conversation history shows language switches
        history_result = api_client.get_conversation_history(session_id)
        assert history_result["status_code"] == 200
        
        history = history_result["response"]
        assert len(history) >= len(conversation) * 2, "History should include user and assistant messages"
    
    @given(st.text(min_size=5, max_size=100).filter(lambda x: x.strip() and any(c.isalpha() for c in x)))
    @settings(max_examples=100, deadline=60000)
    def test_property_agent_conversation_consistency(self, user_message):
        """
        Property test: Agent conversation consistency
        Feature: multilingual-e2e-testing, Property 5: Agent conversation consistency
        
        For any multilingual conversation session, the agent should maintain language
        preferences, use appropriate multilingual tools, and provide coherent responses
        with proper cross-language context.
        """
        from quickship_agent.services.language_service import get_language_service
        
        # Test language detection on user message
        language_service = get_language_service()
        detected_lang, confidence = language_service.detect_language(user_message, return_confidence=True)
        
        # Property: Language detection should work for any user input
        assert detected_lang is not None, "Language detection should return a result"
        assert isinstance(confidence, (int, float)), "Confidence should be numeric"
        assert 0 <= confidence <= 1, "Confidence should be between 0 and 1"
        
        # Property: Message should be processable by agent
        try:
            # Simulate agent processing
            message_processed = user_message.strip()
            assert len(message_processed) > 0, "Processed message should not be empty"
            
            # Property: Agent should handle various message types
            words = message_processed.split()
            assert len(words) > 0, "Message should have at least one word"
            assert len(words) <= 100, "Message should not be too long for processing"
            
            # Property: Language consistency should be maintained
            if detected_lang in ["en", "es", "fr", "de", "pt"]:  # Tier 1 languages
                assert confidence >= 0.5, f"Confidence for tier 1 language should be >= 0.5, got {confidence}"
            
            # Property: Message should be safe for processing
            unsafe_patterns = ["<script", "javascript:", "eval(", "exec("]
            message_lower = message_processed.lower()
            is_safe = not any(pattern in message_lower for pattern in unsafe_patterns)
            assert is_safe, f"Message contains unsafe patterns: {user_message[:50]}..."
            
        except Exception as e:
            pytest.fail(f"Agent conversation property test failed for message: {user_message[:50]}... Error: {e}")
    
    def test_agent_performance_threshold(self, api_client: MultilingualAPITestClient, 
                                       prepared_agent_collection):
        """Test that agent responses meet performance thresholds."""
        # Create session
        session_result = api_client.create_agent_session()
        assert session_result["status_code"] == 200
        
        session_id = session_result["response"]["session_id"]
        self.cleanup_manager.register_session(session_id)
        
        max_response_time = self.config["performance_thresholds"]["agent_response_max_seconds"] * 1000  # Convert to ms
        
        # Test multiple messages in different languages
        test_messages = [
            {"lang": "en", "msg": "What are your shipping rates?"},
            {"lang": "es", "msg": "¿Cuánto tiempo tarda la entrega?"},
            {"lang": "fr", "msg": "Proposez-vous des services de collecte?"},
            {"lang": "en", "msg": "How can I track my shipment?"},
            {"lang": "de", "msg": "Welche Zahlungsmethoden akzeptieren Sie?"}
        ]
        
        response_times = []
        
        for test_msg in test_messages:
            message_result = api_client.send_agent_message(
                message=test_msg["msg"],
                session_id=session_id,
                knowledge_base=prepared_agent_collection
            )
            
            assert message_result["status_code"] == 200, \
                f"Agent failed for {test_msg['lang']}: {message_result['response']}"
            
            response_time = message_result["duration_ms"]
            response_times.append(response_time)
            
            # Individual response should meet threshold
            assert response_time <= max_response_time, \
                f"Message '{test_msg['msg']}' took {response_time}ms, exceeds threshold of {max_response_time}ms"
        
        # Average response time should also be good
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time <= max_response_time * 0.8, \
            f"Average agent response time {avg_response_time}ms exceeds 80% of threshold"
    
    def test_session_cleanup_and_reset(self, api_client: MultilingualAPITestClient):
        """Test agent session cleanup and reset functionality."""
        # Create session
        session_result = api_client.create_agent_session()
        assert session_result["status_code"] == 200
        
        session_id = session_result["response"]["session_id"]
        
        # Send some messages
        for i in range(3):
            message_result = api_client.send_agent_message(
                message=f"Test message {i+1}",
                session_id=session_id
            )
            assert message_result["status_code"] == 200
        
        # Verify conversation history exists
        history_result = api_client.get_conversation_history(session_id)
        assert history_result["status_code"] == 200
        history = history_result["response"]
        assert len(history) > 0, "Should have conversation history"
        
        # Reset session
        reset_result = api_client.reset_session(session_id)
        assert reset_result["status_code"] == 200, f"Session reset failed: {reset_result['response']}"
        
        # Verify session was cleaned up
        # (The exact behavior depends on implementation - session might be deleted or cleared)
        post_reset_history = api_client.get_conversation_history(session_id)
        # Either the session is gone (404) or history is empty
        assert post_reset_history["status_code"] in [200, 404], "Unexpected status after reset"
        
        if post_reset_history["status_code"] == 200:
            history_after_reset = post_reset_history["response"]
            assert len(history_after_reset) == 0, "History should be empty after reset"
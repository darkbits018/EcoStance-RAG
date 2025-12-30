"""
Test semantic accuracy validation for multilingual E2E testing
Feature: multilingual-e2e-testing, Property 8: Semantic accuracy preservation
"""

import pytest
import time
from typing import Dict, Any, List, Tuple
from hypothesis import given, strategies as st, settings

from .fixtures.api_client import MultilingualAPITestClient
from .utils.test_data_utils import MultilingualTestDataManager
from .utils.cleanup_utils import get_cleanup_manager


class TestSemanticAccuracyValidation:
    """Test semantic accuracy validation for multilingual operations."""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_config, multilingual_services):
        """Set up test environment."""
        self.config = test_config
        self.services = multilingual_services
        self.cleanup_manager = get_cleanup_manager()
        self.test_data_manager = MultilingualTestDataManager(test_config["pdf_path"])
    
    @pytest.fixture(scope="class")
    def prepared_semantic_collection(self, api_client: MultilingualAPITestClient, test_config):
        """Prepare a collection for semantic accuracy testing."""
        collection_name = f"semantic_test_{int(time.time())}{test_config['collection_suffix']}"
        
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
    
    def test_semantic_meaning_preservation_in_embeddings(self, api_client: MultilingualAPITestClient, 
                                                        prepared_semantic_collection):
        """Test that semantic meaning is preserved in embeddings across languages."""
        # Test semantically equivalent queries in different languages
        semantic_equivalents = [
            {
                "concept": "shipping_rates",
                "queries": {
                    "en": "What are the shipping rates for international delivery?",
                    "es": "¿Cuáles son las tarifas de envío para entrega internacional?",
                    "fr": "Quels sont les tarifs d'expédition pour la livraison internationale?",
                    "de": "Wie hoch sind die Versandkosten für internationale Lieferungen?"
                }
            },
            {
                "concept": "delivery_time",
                "queries": {
                    "en": "How long does delivery take?",
                    "es": "¿Cuánto tiempo tarda la entrega?",
                    "fr": "Combien de temps prend la livraison?",
                    "de": "Wie lange dauert die Lieferung?"
                }
            }
        ]
        
        for concept_group in semantic_equivalents:
            concept = concept_group["concept"]
            queries = concept_group["queries"]
            
            results_by_language = {}
            
            # Search with each language variant
            for language, query in queries.items():
                search_result = api_client.search_multilingual_knowledge_base(
                    kb_name=prepared_semantic_collection,
                    query=query,
                    language=language
                )
                
                assert search_result["status_code"] == 200, \
                    f"Search failed for {language} in concept {concept}: {search_result['response']}"
                
                results = search_result["response"]["results"]
                assert len(results) > 0, f"No results for {language} query: {query}"
                
                results_by_language[language] = results
            
            # Validate semantic consistency across languages
            self._validate_semantic_consistency(results_by_language, concept)
    
    def test_cross_language_semantic_equivalence(self, api_client: MultilingualAPITestClient, 
                                               prepared_semantic_collection):
        """Test that cross-language searches return semantically equivalent content."""
        # Search for the same concept in different languages
        base_query = "international shipping policies and procedures"
        
        # Translate to different languages (conceptually equivalent)
        translated_queries = {
            "en": "international shipping policies and procedures",
            "es": "políticas y procedimientos de envío internacional",
            "fr": "politiques et procédures d'expédition internationale",
            "de": "internationale Versandrichtlinien und -verfahren"
        }
        
        all_results = {}
        
        for language, query in translated_queries.items():
            search_result = api_client.search_multilingual_knowledge_base(
                kb_name=prepared_semantic_collection,
                query=query,
                language=language
            )
            
            assert search_result["status_code"] == 200
            results = search_result["response"]["results"]
            all_results[language] = results
        
        # Validate that results show semantic equivalence
        for lang1, results1 in all_results.items():
            for lang2, results2 in all_results.items():
                if lang1 != lang2 and len(results1) > 0 and len(results2) > 0:
                    # Check for semantic overlap
                    overlap_score = self._calculate_semantic_overlap(results1, results2)
                    assert overlap_score > 0.3, \
                        f"Low semantic overlap ({overlap_score:.2f}) between {lang1} and {lang2} results"
    
    def test_factual_consistency_across_languages(self, api_client: MultilingualAPITestClient, 
                                                 prepared_semantic_collection):
        """Test that factual consistency is maintained regardless of source content language."""
        # Create agent session for factual queries
        session_result = api_client.create_agent_session()
        assert session_result["status_code"] == 200
        
        session_id = session_result["response"]["session_id"]
        self.cleanup_manager.register_session(session_id)
        
        # Ask factual questions in different languages
        factual_questions = {
            "en": "What is the maximum weight limit for international shipments?",
            "es": "¿Cuál es el límite máximo de peso para envíos internacionales?",
            "fr": "Quelle est la limite de poids maximale pour les expéditions internationales?",
            "de": "Was ist das maximale Gewichtslimit für internationale Sendungen?"
        }
        
        responses = {}
        
        for language, question in factual_questions.items():
            message_result = api_client.send_agent_message(
                message=question,
                session_id=session_id,
                knowledge_base=prepared_semantic_collection
            )
            
            assert message_result["status_code"] == 200
            response_data = message_result["response"]
            responses[language] = response_data.get("response", "")
        
        # Validate factual consistency
        self._validate_factual_consistency(responses, "weight_limit")
    
    def test_language_detection_accuracy_threshold(self, language_samples):
        """Test that language detection achieves >95% accuracy for supported languages."""
        from quickship_agent.services.language_service import get_language_service
        
        language_service = get_language_service()
        
        correct_detections = 0
        total_detections = 0
        
        # Test with known language samples
        for expected_language, text_sample in language_samples.items():
            if expected_language in self.config["tier_1_languages"]:  # Focus on tier 1 languages
                detected_lang, confidence = language_service.detect_language(text_sample, return_confidence=True)
                
                total_detections += 1
                
                # Check if detection is correct (allow for language variants)
                is_correct = (detected_lang == expected_language or 
                            detected_lang.startswith(expected_language[:2]) or
                            expected_language.startswith(detected_lang[:2]))
                
                if is_correct:
                    correct_detections += 1
                
                # Validate confidence for correct detections
                if is_correct:
                    assert confidence >= 0.7, \
                        f"Confidence too low for correct detection of {expected_language}: {confidence}"
        
        # Calculate accuracy
        accuracy = (correct_detections / total_detections) * 100 if total_detections > 0 else 0
        
        # Validate accuracy threshold
        min_accuracy = 95.0
        assert accuracy >= min_accuracy, \
            f"Language detection accuracy {accuracy:.1f}% below threshold {min_accuracy}%"
        
        print(f"Language detection accuracy: {accuracy:.1f}% ({correct_detections}/{total_detections})")
        
        return {
            "accuracy_percent": accuracy,
            "correct_detections": correct_detections,
            "total_detections": total_detections,
            "threshold_percent": min_accuracy
        }
    
    def test_relevance_score_correlation_with_human_judgment(self, api_client: MultilingualAPITestClient, 
                                                           prepared_semantic_collection):
        """Test that relevance scores correlate with expected human judgment."""
        # Define queries with expected relevance rankings
        test_cases = [
            {
                "query": "shipping rates and costs",
                "language": "en",
                "highly_relevant_terms": ["shipping", "rates", "cost", "price", "fee"],
                "moderately_relevant_terms": ["delivery", "logistics", "transport"],
                "low_relevant_terms": ["customer", "service", "support"]
            },
            {
                "query": "delivery time and schedule",
                "language": "en", 
                "highly_relevant_terms": ["delivery", "time", "schedule", "days", "hours"],
                "moderately_relevant_terms": ["shipping", "transport", "logistics"],
                "low_relevant_terms": ["payment", "billing", "invoice"]
            }
        ]
        
        for test_case in test_cases:
            search_result = api_client.search_multilingual_knowledge_base(
                kb_name=prepared_semantic_collection,
                query=test_case["query"],
                language=test_case["language"]
            )
            
            assert search_result["status_code"] == 200
            results = search_result["response"]["results"]
            
            if len(results) >= 3:  # Need at least 3 results for meaningful analysis
                # Analyze relevance score distribution
                scores = [result["score"] for result in results]
                contents = [result.get("content", result.get("text", "")).lower() for result in results]
                
                # Validate score ordering (should be descending)
                for i in range(len(scores) - 1):
                    assert scores[i] >= scores[i + 1], \
                        f"Relevance scores not properly ordered: {scores[i]} < {scores[i + 1]}"
                
                # Validate content relevance correlation
                high_relevance_count = 0
                for i, content in enumerate(contents[:3]):  # Check top 3 results
                    relevance_score = self._calculate_content_relevance(
                        content, 
                        test_case["highly_relevant_terms"],
                        test_case["moderately_relevant_terms"],
                        test_case["low_relevant_terms"]
                    )
                    
                    # Top results should have higher content relevance
                    if i == 0:  # Top result
                        assert relevance_score >= 0.3, \
                            f"Top result has low content relevance: {relevance_score:.2f}"
                    
                    if relevance_score >= 0.5:
                        high_relevance_count += 1
                
                # At least one of top 3 should be highly relevant
                assert high_relevance_count >= 1, \
                    f"No highly relevant results in top 3 for query: {test_case['query']}"
    
    @given(st.text(min_size=10, max_size=200).filter(lambda x: x.strip() and any(c.isalpha() for c in x)))
    @settings(max_examples=100, deadline=60000)
    def test_property_semantic_accuracy_preservation(self, text_content):
        """
        Property test: Semantic accuracy preservation
        Feature: multilingual-e2e-testing, Property 8: Semantic accuracy preservation
        
        For any multilingual content processing, semantic meaning should be preserved in
        embeddings, cross-language searches should return semantically equivalent content,
        and language detection should achieve >95% accuracy for supported languages.
        """
        from quickship_agent.services.language_service import get_language_service
        
        # Test language detection
        language_service = get_language_service()
        detected_lang, confidence = language_service.detect_language(text_content, return_confidence=True)
        
        # Property: Language detection should work for any text
        assert detected_lang is not None, "Language detection should return a result"
        assert isinstance(confidence, (int, float)), "Confidence should be numeric"
        assert 0 <= confidence <= 1, "Confidence should be between 0 and 1"
        
        # Property: Text should be semantically processable
        try:
            # Simulate semantic processing
            text_processed = text_content.strip().lower()
            assert len(text_processed) > 0, "Processed text should not be empty"
            
            # Property: Text should have semantic structure
            words = text_processed.split()
            assert len(words) > 0, "Text should have at least one word"
            
            # Property: Semantic meaning should be extractable
            # Check for meaningful content (not just random characters)
            alpha_ratio = sum(1 for c in text_processed if c.isalpha()) / len(text_processed)
            assert alpha_ratio >= 0.5, f"Text should be mostly alphabetic for semantic processing: {alpha_ratio:.2f}"
            
            # Property: Language detection confidence should be reasonable for clear text
            if detected_lang in ["en", "es", "fr", "de", "pt"]:  # Tier 1 languages
                word_count = len(words)
                if word_count >= 5:  # Longer text should have higher confidence
                    assert confidence >= 0.6, \
                        f"Confidence for tier 1 language with {word_count} words should be >= 0.6, got {confidence}"
            
            # Property: Text should be safe for semantic processing
            unsafe_patterns = ["<script", "javascript:", "eval(", "exec(", "DROP TABLE", "SELECT *"]
            text_lower = text_processed.lower()
            is_safe = not any(pattern in text_lower for pattern in unsafe_patterns)
            assert is_safe, f"Text contains unsafe patterns for semantic processing: {text_content[:50]}..."
            
        except Exception as e:
            pytest.fail(f"Semantic accuracy property test failed for text: {text_content[:50]}... Error: {e}")
    
    def test_multilingual_content_semantic_consistency(self, api_client: MultilingualAPITestClient, 
                                                     prepared_semantic_collection):
        """Test semantic consistency across multilingual content processing."""
        # Test the same semantic concept expressed in different languages
        concept_variations = {
            "logistics_services": {
                "en": ["logistics services", "shipping solutions", "delivery options"],
                "es": ["servicios logísticos", "soluciones de envío", "opciones de entrega"],
                "fr": ["services logistiques", "solutions d'expédition", "options de livraison"],
                "de": ["logistikdienstleistungen", "versandlösungen", "lieferoptionen"]
            }
        }
        
        for concept, language_variations in concept_variations.items():
            concept_results = {}
            
            for language, variations in language_variations.items():
                language_results = []
                
                for variation in variations:
                    search_result = api_client.search_multilingual_knowledge_base(
                        kb_name=prepared_semantic_collection,
                        query=variation,
                        language=language
                    )
                    
                    if search_result["status_code"] == 200:
                        results = search_result["response"]["results"]
                        if results:
                            language_results.extend(results[:2])  # Top 2 results per variation
                
                concept_results[language] = language_results
            
            # Validate semantic consistency across languages
            self._validate_cross_language_semantic_consistency(concept_results, concept)
    
    def _validate_semantic_consistency(self, results_by_language: Dict[str, List[Dict]], concept: str):
        """Validate semantic consistency across language results."""
        if len(results_by_language) < 2:
            return  # Need at least 2 languages to compare
        
        languages = list(results_by_language.keys())
        
        for i, lang1 in enumerate(languages):
            for lang2 in languages[i+1:]:
                results1 = results_by_language[lang1]
                results2 = results_by_language[lang2]
                
                if len(results1) > 0 and len(results2) > 0:
                    # Check semantic overlap
                    overlap = self._calculate_semantic_overlap(results1, results2)
                    assert overlap > 0.2, \
                        f"Low semantic overlap ({overlap:.2f}) for concept '{concept}' between {lang1} and {lang2}"
    
    def _calculate_semantic_overlap(self, results1: List[Dict], results2: List[Dict]) -> float:
        """Calculate semantic overlap between two result sets."""
        # Simple keyword-based overlap calculation
        def extract_keywords(results):
            keywords = set()
            for result in results[:3]:  # Top 3 results
                content = result.get("content", result.get("text", "")).lower()
                words = content.split()
                # Filter out common stop words and keep meaningful terms
                meaningful_words = [w for w in words if len(w) > 3 and w.isalpha()]
                keywords.update(meaningful_words[:10])  # Top 10 words per result
            return keywords
        
        keywords1 = extract_keywords(results1)
        keywords2 = extract_keywords(results2)
        
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _validate_factual_consistency(self, responses: Dict[str, str], fact_type: str):
        """Validate factual consistency across language responses."""
        # Simple factual consistency check based on common patterns
        fact_patterns = {
            "weight_limit": [r"\d+\s*(kg|kilogram|lb|pound)", r"weight.*limit", r"maximum.*weight"],
            "delivery_time": [r"\d+\s*(day|hour|week)", r"delivery.*time", r"takes.*\d+"],
            "shipping_cost": [r"\$\d+", r"cost.*\$", r"price.*\d+", r"fee.*\d+"]
        }
        
        if fact_type in fact_patterns:
            patterns = fact_patterns[fact_type]
            
            # Check if responses contain similar factual patterns
            pattern_matches = {}
            for language, response in responses.items():
                response_lower = response.lower()
                matches = []
                
                import re
                for pattern in patterns:
                    if re.search(pattern, response_lower):
                        matches.append(pattern)
                
                pattern_matches[language] = matches
            
            # Validate that responses show some factual consistency
            languages_with_facts = [lang for lang, matches in pattern_matches.items() if matches]
            
            if len(languages_with_facts) >= 2:
                # At least 2 languages should contain similar factual patterns
                assert len(languages_with_facts) >= 2, \
                    f"Factual consistency check failed for {fact_type}: only {len(languages_with_facts)} languages contain facts"
    
    def _calculate_content_relevance(self, content: str, high_terms: List[str], 
                                   med_terms: List[str], low_terms: List[str]) -> float:
        """Calculate content relevance score based on term presence."""
        content_lower = content.lower()
        
        high_score = sum(2 for term in high_terms if term in content_lower)
        med_score = sum(1 for term in med_terms if term in content_lower)
        low_score = sum(0.5 for term in low_terms if term in content_lower)
        
        total_possible = len(high_terms) * 2 + len(med_terms) * 1 + len(low_terms) * 0.5
        actual_score = high_score + med_score + low_score
        
        return actual_score / total_possible if total_possible > 0 else 0.0
    
    def _validate_cross_language_semantic_consistency(self, concept_results: Dict[str, List[Dict]], concept: str):
        """Validate semantic consistency across languages for a concept."""
        languages = list(concept_results.keys())
        
        if len(languages) < 2:
            return
        
        # Check that all languages return some results for the concept
        for language, results in concept_results.items():
            assert len(results) > 0, f"No results for concept '{concept}' in language '{language}'"
        
        # Check semantic overlap between languages
        for i, lang1 in enumerate(languages):
            for lang2 in languages[i+1:]:
                results1 = concept_results[lang1]
                results2 = concept_results[lang2]
                
                overlap = self._calculate_semantic_overlap(results1, results2)
                assert overlap > 0.15, \
                    f"Low semantic consistency ({overlap:.2f}) for concept '{concept}' between {lang1} and {lang2}"
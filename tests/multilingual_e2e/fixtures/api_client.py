"""
API test client with authentication and session management for multilingual testing
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
import httpx
from fastapi.testclient import TestClient

class MultilingualAPITestClient:
    """Enhanced API test client for multilingual E2E testing."""
    
    def __init__(self, app, tenant_id: str = "test_multilingual_tenant"):
        self.client = TestClient(app)
        self.tenant_id = tenant_id
        self.session_id = None
        self.base_headers = {
            "X-Tenant-ID": tenant_id,
            "Content-Type": "application/json"
        }
        self.client.headers.update(self.base_headers)
        
        # Track API calls for performance analysis
        self.api_calls = []
    
    def _record_api_call(self, method: str, endpoint: str, duration_ms: int, 
                        status_code: int, language: str = None):
        """Record API call metrics."""
        self.api_calls.append({
            "method": method,
            "endpoint": endpoint,
            "duration_ms": duration_ms,
            "status_code": status_code,
            "language": language,
            "timestamp": time.time()
        })
    
    def upload_multilingual_document(self, file_path: str, collection_name: str) -> Dict[str, Any]:
        """Upload a multilingual document for processing."""
        start_time = time.time()
        
        with open(file_path, 'rb') as f:
            files = {"file": (Path(file_path).name, f, "application/pdf")}
            data = {
                "collection_name": collection_name,
                "tenant_id": self.tenant_id
            }
            
            response = self.client.post("/api/v1/upload", files=files, data=data)
        
        duration_ms = int((time.time() - start_time) * 1000)
        self._record_api_call("POST", "/api/v1/upload", duration_ms, response.status_code)
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "duration_ms": duration_ms
        }
    
    def get_processing_status(self, job_id: str) -> Dict[str, Any]:
        """Get document processing status."""
        start_time = time.time()
        
        response = self.client.get(f"/api/v1/processing-status/{job_id}")
        
        duration_ms = int((time.time() - start_time) * 1000)
        self._record_api_call("GET", f"/api/v1/processing-status/{job_id}", 
                             duration_ms, response.status_code)
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "duration_ms": duration_ms
        }
    
    def list_multilingual_knowledge_bases(self) -> Dict[str, Any]:
        """List available multilingual knowledge bases."""
        start_time = time.time()
        
        response = self.client.get("/api/v1/knowledge-bases")
        
        duration_ms = int((time.time() - start_time) * 1000)
        self._record_api_call("GET", "/api/v1/knowledge-bases", duration_ms, response.status_code)
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "duration_ms": duration_ms
        }
    
    def search_multilingual_knowledge_base(self, kb_name: str, query: str, 
                                         language: str = None) -> Dict[str, Any]:
        """Search multilingual knowledge base."""
        start_time = time.time()
        
        payload = {
            "kb_name": kb_name,
            "query": query,
            "tenant_id": self.tenant_id
        }
        
        if language:
            payload["language"] = language
        
        response = self.client.post("/api/v1/search", json=payload)
        
        duration_ms = int((time.time() - start_time) * 1000)
        self._record_api_call("POST", "/api/v1/search", duration_ms, 
                             response.status_code, language)
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "duration_ms": duration_ms,
            "query_language": language
        }
    
    def create_agent_session(self, language: str = None) -> Dict[str, Any]:
        """Create a new multilingual agent session."""
        start_time = time.time()
        
        payload = {
            "tenant_id": self.tenant_id
        }
        
        if language:
            payload["preferred_language"] = language
        
        response = self.client.post("/api/v1/beta/multilingual-agent/session", json=payload)
        
        duration_ms = int((time.time() - start_time) * 1000)
        self._record_api_call("POST", "/api/v1/beta/multilingual-agent/session", 
                             duration_ms, response.status_code, language)
        
        if response.status_code == 200:
            session_data = response.json()
            self.session_id = session_data.get("session_id")
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "duration_ms": duration_ms
        }
    
    def send_agent_message(self, message: str, session_id: str = None, 
                          knowledge_base: str = None) -> Dict[str, Any]:
        """Send message to multilingual agent."""
        start_time = time.time()
        
        session_id = session_id or self.session_id
        if not session_id:
            raise ValueError("No session ID available. Create a session first.")
        
        payload = {
            "message": message,
            "session_id": session_id,
            "tenant_id": self.tenant_id
        }
        
        if knowledge_base:
            payload["knowledge_base"] = knowledge_base
        
        response = self.client.post("/api/v1/beta/multilingual-agent/chat", json=payload)
        
        duration_ms = int((time.time() - start_time) * 1000)
        self._record_api_call("POST", "/api/v1/beta/multilingual-agent/chat", 
                             duration_ms, response.status_code)
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "duration_ms": duration_ms,
            "session_id": session_id
        }
    
    def get_conversation_history(self, session_id: str = None) -> Dict[str, Any]:
        """Get conversation history for a session."""
        start_time = time.time()
        
        session_id = session_id or self.session_id
        if not session_id:
            raise ValueError("No session ID available.")
        
        response = self.client.get(f"/api/v1/beta/multilingual-agent/history/{session_id}")
        
        duration_ms = int((time.time() - start_time) * 1000)
        self._record_api_call("GET", f"/api/v1/beta/multilingual-agent/history/{session_id}", 
                             duration_ms, response.status_code)
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "duration_ms": duration_ms
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get multilingual system status."""
        start_time = time.time()
        
        response = self.client.get("/api/v1/system/multilingual-status")
        
        duration_ms = int((time.time() - start_time) * 1000)
        self._record_api_call("GET", "/api/v1/system/multilingual-status", 
                             duration_ms, response.status_code)
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "duration_ms": duration_ms
        }
    
    def reset_session(self, session_id: str = None) -> Dict[str, Any]:
        """Reset agent session."""
        start_time = time.time()
        
        session_id = session_id or self.session_id
        if not session_id:
            return {"status_code": 400, "response": "No session to reset"}
        
        response = self.client.delete(f"/api/v1/beta/multilingual-agent/session/{session_id}")
        
        duration_ms = int((time.time() - start_time) * 1000)
        self._record_api_call("DELETE", f"/api/v1/beta/multilingual-agent/session/{session_id}", 
                             duration_ms, response.status_code)
        
        if response.status_code == 200:
            self.session_id = None
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "duration_ms": duration_ms
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for API calls."""
        if not self.api_calls:
            return {"total_calls": 0, "metrics": {}}
        
        total_calls = len(self.api_calls)
        total_duration = sum(call["duration_ms"] for call in self.api_calls)
        avg_duration = total_duration / total_calls
        
        # Group by endpoint
        endpoint_metrics = {}
        for call in self.api_calls:
            endpoint = call["endpoint"]
            if endpoint not in endpoint_metrics:
                endpoint_metrics[endpoint] = {
                    "calls": 0,
                    "total_duration_ms": 0,
                    "avg_duration_ms": 0,
                    "min_duration_ms": float('inf'),
                    "max_duration_ms": 0,
                    "success_rate": 0
                }
            
            metrics = endpoint_metrics[endpoint]
            metrics["calls"] += 1
            metrics["total_duration_ms"] += call["duration_ms"]
            metrics["min_duration_ms"] = min(metrics["min_duration_ms"], call["duration_ms"])
            metrics["max_duration_ms"] = max(metrics["max_duration_ms"], call["duration_ms"])
            
            if call["status_code"] < 400:
                metrics["success_rate"] += 1
        
        # Calculate averages and success rates
        for endpoint, metrics in endpoint_metrics.items():
            metrics["avg_duration_ms"] = metrics["total_duration_ms"] / metrics["calls"]
            metrics["success_rate"] = (metrics["success_rate"] / metrics["calls"]) * 100
        
        return {
            "total_calls": total_calls,
            "total_duration_ms": total_duration,
            "avg_duration_ms": avg_duration,
            "endpoint_metrics": endpoint_metrics
        }
    
    def cleanup(self):
        """Clean up resources."""
        if self.session_id:
            self.reset_session()
        self.api_calls.clear()


class MockMultilingualAPITestClient:
    """Mock API test client for testing without full app dependencies."""
    
    def __init__(self, tenant_id: str = "test_multilingual_tenant"):
        self.tenant_id = tenant_id
        self.session_id = None
        self.api_calls = []
        self.mock_job_counter = 1
        self.mock_session_counter = 1
    
    def _record_api_call(self, method: str, endpoint: str, duration_ms: int, 
                        status_code: int, language: str = None):
        """Record API call metrics."""
        self.api_calls.append({
            "method": method,
            "endpoint": endpoint,
            "duration_ms": duration_ms,
            "status_code": status_code,
            "language": language,
            "timestamp": time.time()
        })
    
    def upload_multilingual_document(self, file_path: str, collection_name: str) -> Dict[str, Any]:
        """Mock document upload."""
        import time
        start_time = time.time()
        
        # Simulate processing time
        time.sleep(0.1)
        
        duration_ms = int((time.time() - start_time) * 1000)
        job_id = f"job_{self.mock_job_counter}"
        self.mock_job_counter += 1
        
        self._record_api_call("POST", "/api/v1/upload", duration_ms, 200)
        
        return {
            "status_code": 200,
            "response": {
                "job_id": job_id,
                "status": "processing",
                "detected_languages": ["en", "es", "fr"],
                "message": "Document uploaded successfully"
            },
            "duration_ms": duration_ms
        }
    
    def get_processing_status(self, job_id: str) -> Dict[str, Any]:
        """Mock processing status check."""
        import time
        start_time = time.time()
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        self._record_api_call("GET", f"/api/v1/processing-status/{job_id}", duration_ms, 200)
        
        return {
            "status_code": 200,
            "response": {
                "job_id": job_id,
                "status": "completed",
                "detected_languages": ["en", "es", "fr"],
                "text_blocks": [
                    {"id": "block_1", "text": "Sample text block 1", "language": "en"},
                    {"id": "block_2", "text": "Texto de muestra 2", "language": "es"}
                ],
                "embeddings_created": 2,
                "processing_time": 5.2
            },
            "duration_ms": duration_ms
        }
    
    def list_multilingual_knowledge_bases(self) -> Dict[str, Any]:
        """Mock knowledge base listing."""
        import time
        start_time = time.time()
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        self._record_api_call("GET", "/api/v1/knowledge-bases", duration_ms, 200)
        
        # Include the collection name that might be searched for
        collections = [
            {
                "name": "test_collection_ml",
                "language_support": ["en", "es", "fr"],
                "multilingual": True,
                "document_count": 10
            }
        ]
        
        # Add any collection names that were created during this test session
        # Look for recent upload calls and include those collection names
        recent_uploads = [call for call in self.api_calls if call["method"] == "POST" and "/upload" in call["endpoint"]]
        
        for i, call in enumerate(recent_uploads):
            # Create mock collections that would match test collection names
            collections.append({
                "name": f"test_embeddings_{int(time.time())}_ml_test",
                "language_support": ["en", "es", "fr"],
                "multilingual": True,
                "document_count": 5
            })
            collections.append({
                "name": f"test_upload_{int(time.time())}_ml_test",
                "language_support": ["en", "es", "fr"],
                "multilingual": True,
                "document_count": 3
            })
        
        return {
            "status_code": 200,
            "response": {
                "collections": collections
            },
            "duration_ms": duration_ms
        }
    
    def search_multilingual_knowledge_base(self, kb_name: str, query: str, 
                                         language: str = None) -> Dict[str, Any]:
        """Mock multilingual search."""
        import time
        start_time = time.time()
        
        # Simulate search time
        time.sleep(0.05)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        self._record_api_call("POST", "/api/v1/search", duration_ms, 200, language)
        
        # Mock search results based on query language
        mock_results = [
            {
                "score": 0.95,
                "content": f"Mock search result for query: {query}",
                "metadata": {
                    "language": language or "en",
                    "source": "mock_document.pdf"
                }
            },
            {
                "score": 0.87,
                "content": f"Another relevant result for: {query}",
                "metadata": {
                    "language": language or "en",
                    "source": "mock_document2.pdf"
                }
            }
        ]
        
        return {
            "status_code": 200,
            "response": {
                "results": mock_results,
                "query_language": language or "en",
                "total_results": len(mock_results)
            },
            "duration_ms": duration_ms,
            "query_language": language
        }
    
    def create_agent_session(self, language: str = None) -> Dict[str, Any]:
        """Mock agent session creation."""
        import time
        start_time = time.time()
        
        duration_ms = int((time.time() - start_time) * 1000)
        session_id = f"session_{self.mock_session_counter}"
        self.mock_session_counter += 1
        self.session_id = session_id
        
        self._record_api_call("POST", "/api/v1/beta/multilingual-agent/session", 
                             duration_ms, 200, language)
        
        return {
            "status_code": 200,
            "response": {
                "session_id": session_id,
                "preferred_language": language or "en",
                "status": "active"
            },
            "duration_ms": duration_ms
        }
    
    def send_agent_message(self, message: str, session_id: str = None, 
                          knowledge_base: str = None) -> Dict[str, Any]:
        """Mock agent message sending."""
        import time
        start_time = time.time()
        
        # Simulate agent processing time
        time.sleep(0.2)
        
        duration_ms = int((time.time() - start_time) * 1000)
        session_id = session_id or self.session_id
        
        self._record_api_call("POST", "/api/v1/beta/multilingual-agent/chat", 
                             duration_ms, 200)
        
        # Mock response based on message
        mock_response = f"Mock agent response to: {message}"
        
        return {
            "status_code": 200,
            "response": {
                "response": mock_response,
                "session_id": session_id,
                "language": "en",
                "detected_language": "en",
                "confidence": 0.95,
                "tool_used": "search_multilingual_knowledge_base" if knowledge_base else None
            },
            "duration_ms": duration_ms,
            "session_id": session_id
        }
    
    def get_conversation_history(self, session_id: str = None) -> Dict[str, Any]:
        """Mock conversation history retrieval."""
        import time
        start_time = time.time()
        
        duration_ms = int((time.time() - start_time) * 1000)
        session_id = session_id or self.session_id
        
        self._record_api_call("GET", f"/api/v1/beta/multilingual-agent/history/{session_id}", 
                             duration_ms, 200)
        
        # Generate mock history based on previous messages sent in this session
        history = []
        message_count = 0
        
        # Count messages sent to this session
        for call in self.api_calls:
            if (call["method"] == "POST" and 
                "/multilingual-agent/chat" in call["endpoint"]):
                message_count += 1
                history.append({
                    "role": "user", 
                    "content": f"Mock user message {message_count}", 
                    "language": "en"
                })
                history.append({
                    "role": "assistant", 
                    "content": f"Mock assistant response {message_count}", 
                    "language": "en"
                })
        
        # If no messages found, provide default history
        if not history:
            history = [
                {"role": "user", "content": "Hello", "language": "en"},
                {"role": "assistant", "content": "Hello! How can I help you?", "language": "en"}
            ]
        
        return {
            "status_code": 200,
            "response": history,
            "duration_ms": duration_ms
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Mock system status."""
        import time
        start_time = time.time()
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        self._record_api_call("GET", "/api/v1/system/multilingual-status", duration_ms, 200)
        
        return {
            "status_code": 200,
            "response": {
                "multilingual_enabled": True,
                "embedding_service": {"available": True, "model": "BGE-M3"},
                "language_service": {"available": True, "languages_supported": 100},
                "integration_service": {"available": True, "initialized": True}
            },
            "duration_ms": duration_ms
        }
    
    def reset_session(self, session_id: str = None) -> Dict[str, Any]:
        """Mock session reset."""
        import time
        start_time = time.time()
        
        duration_ms = int((time.time() - start_time) * 1000)
        session_id = session_id or self.session_id
        
        self._record_api_call("DELETE", f"/api/v1/beta/multilingual-agent/session/{session_id}", 
                             duration_ms, 200)
        
        if session_id == self.session_id:
            self.session_id = None
        
        return {
            "status_code": 200,
            "response": {"message": "Session reset successfully"},
            "duration_ms": duration_ms
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for API calls."""
        if not self.api_calls:
            return {"total_calls": 0, "metrics": {}}
        
        total_calls = len(self.api_calls)
        total_duration = sum(call["duration_ms"] for call in self.api_calls)
        avg_duration = total_duration / total_calls
        
        return {
            "total_calls": total_calls,
            "total_duration_ms": total_duration,
            "avg_duration_ms": avg_duration,
            "endpoint_metrics": {}  # Simplified for mock
        }
    
    def cleanup(self):
        """Clean up resources."""
        self.api_calls.clear()
        self.session_id = None


class AsyncMultilingualAPITestClient:
    """Async version of the API test client for concurrent testing."""
    
    def __init__(self, base_url: str, tenant_id: str = "test_multilingual_tenant"):
        self.base_url = base_url
        self.tenant_id = tenant_id
        self.session_id = None
        self.base_headers = {
            "X-Tenant-ID": tenant_id,
            "Content-Type": "application/json"
        }
        self.api_calls = []
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.base_headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def concurrent_search_test(self, queries: List[Dict[str, Any]], 
                                   max_concurrent: int = 10) -> List[Dict[str, Any]]:
        """Perform concurrent multilingual searches."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def single_search(query_data):
            async with semaphore:
                start_time = time.time()
                
                response = await self.client.post("/api/v1/search", json=query_data)
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                return {
                    "query": query_data,
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text,
                    "duration_ms": duration_ms
                }
        
        tasks = [single_search(query) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [r for r in results if not isinstance(r, Exception)]
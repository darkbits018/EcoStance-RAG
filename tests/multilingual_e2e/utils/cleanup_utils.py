"""
Cleanup utilities for multilingual E2E testing
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class TestCleanupManager:
    """Manage cleanup of test resources."""
    
    def __init__(self):
        self.collections_to_cleanup = []
        self.sessions_to_cleanup = []
        self.temp_files_to_cleanup = []
    
    def register_collection(self, collection_name: str):
        """Register a collection for cleanup."""
        if collection_name not in self.collections_to_cleanup:
            self.collections_to_cleanup.append(collection_name)
    
    def register_session(self, session_id: str):
        """Register a session for cleanup."""
        if session_id not in self.sessions_to_cleanup:
            self.sessions_to_cleanup.append(session_id)
    
    def register_temp_file(self, file_path: str):
        """Register a temporary file for cleanup."""
        if file_path not in self.temp_files_to_cleanup:
            self.temp_files_to_cleanup.append(file_path)
    
    def cleanup_collections(self) -> Dict[str, Any]:
        """Clean up test collections from Qdrant."""
        results = {
            "attempted": len(self.collections_to_cleanup),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        if not self.collections_to_cleanup:
            return results
        
        try:
            from app.services.qdrant_service import QdrantService
            qdrant_service = QdrantService()
            
            for collection_name in self.collections_to_cleanup:
                try:
                    # Check if collection exists before trying to delete
                    if qdrant_service.collection_exists(collection_name):
                        qdrant_service.delete_collection(collection_name)
                        logger.info(f"Deleted test collection: {collection_name}")
                        results["successful"] += 1
                    else:
                        logger.info(f"Collection {collection_name} does not exist, skipping")
                        results["successful"] += 1
                except Exception as e:
                    logger.error(f"Failed to delete collection {collection_name}: {e}")
                    results["failed"] += 1
                    results["errors"].append(f"{collection_name}: {str(e)}")
        
        except ImportError as e:
            logger.error(f"Could not import QdrantService: {e}")
            results["failed"] = results["attempted"]
            results["errors"].append(f"QdrantService import failed: {str(e)}")
        
        self.collections_to_cleanup.clear()
        return results
    
    def cleanup_sessions(self) -> Dict[str, Any]:
        """Clean up test agent sessions."""
        results = {
            "attempted": len(self.sessions_to_cleanup),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        if not self.sessions_to_cleanup:
            return results
        
        try:
            from quickship_agent.multilingual_agent_service import MultilingualAgentService
            
            # Create a temporary agent service for cleanup
            agent_service = MultilingualAgentService(tenant_id="cleanup_service")
            
            for session_id in self.sessions_to_cleanup:
                try:
                    if agent_service.reset_conversation(session_id):
                        logger.info(f"Cleaned up test session: {session_id}")
                        results["successful"] += 1
                    else:
                        logger.info(f"Session {session_id} was already clean")
                        results["successful"] += 1
                except Exception as e:
                    logger.error(f"Failed to cleanup session {session_id}: {e}")
                    results["failed"] += 1
                    results["errors"].append(f"{session_id}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Could not initialize agent service for cleanup: {e}")
            results["failed"] = results["attempted"]
            results["errors"].append(f"Agent service initialization failed: {str(e)}")
        
        self.sessions_to_cleanup.clear()
        return results
    
    def cleanup_temp_files(self) -> Dict[str, Any]:
        """Clean up temporary files."""
        results = {
            "attempted": len(self.temp_files_to_cleanup),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        if not self.temp_files_to_cleanup:
            return results
        
        for file_path in self.temp_files_to_cleanup:
            try:
                path = Path(file_path)
                if path.exists():
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        import shutil
                        shutil.rmtree(path)
                    logger.info(f"Deleted temp file/dir: {file_path}")
                    results["successful"] += 1
                else:
                    logger.info(f"Temp file {file_path} does not exist, skipping")
                    results["successful"] += 1
            except Exception as e:
                logger.error(f"Failed to delete temp file {file_path}: {e}")
                results["failed"] += 1
                results["errors"].append(f"{file_path}: {str(e)}")
        
        self.temp_files_to_cleanup.clear()
        return results
    
    def cleanup_all(self) -> Dict[str, Any]:
        """Clean up all registered resources."""
        results = {
            "collections": self.cleanup_collections(),
            "sessions": self.cleanup_sessions(),
            "temp_files": self.cleanup_temp_files()
        }
        
        total_attempted = sum(r["attempted"] for r in results.values())
        total_successful = sum(r["successful"] for r in results.values())
        total_failed = sum(r["failed"] for r in results.values())
        
        results["summary"] = {
            "total_attempted": total_attempted,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "success_rate": (total_successful / total_attempted * 100) if total_attempted > 0 else 100
        }
        
        return results


# Global cleanup manager instance
_cleanup_manager: Optional[TestCleanupManager] = None

def get_cleanup_manager() -> TestCleanupManager:
    """Get or create the global cleanup manager."""
    global _cleanup_manager
    if _cleanup_manager is None:
        _cleanup_manager = TestCleanupManager()
    return _cleanup_manager

def cleanup_test_collections(collection_names: List[str]) -> Dict[str, Any]:
    """Clean up specific test collections."""
    cleanup_manager = TestCleanupManager()
    for name in collection_names:
        cleanup_manager.register_collection(name)
    return cleanup_manager.cleanup_collections()

def cleanup_test_sessions(session_ids: List[str]) -> Dict[str, Any]:
    """Clean up specific test sessions."""
    cleanup_manager = TestCleanupManager()
    for session_id in session_ids:
        cleanup_manager.register_session(session_id)
    return cleanup_manager.cleanup_sessions()

def cleanup_temp_files(file_paths: List[str]) -> Dict[str, Any]:
    """Clean up specific temporary files."""
    cleanup_manager = TestCleanupManager()
    for file_path in file_paths:
        cleanup_manager.register_temp_file(file_path)
    return cleanup_manager.cleanup_temp_files()

def emergency_cleanup() -> Dict[str, Any]:
    """Emergency cleanup of all known test resources."""
    logger.warning("Performing emergency cleanup of test resources")
    
    results = {
        "collections_cleaned": 0,
        "sessions_cleaned": 0,
        "files_cleaned": 0,
        "errors": []
    }
    
    # Clean up collections with test suffixes
    try:
        from app.services.qdrant_service import QdrantService
        qdrant_service = QdrantService()
        
        # Get all collections and filter for test collections
        collections = qdrant_service.list_collections()
        test_collections = [c for c in collections if "_ml_test" in c or "test_" in c]
        
        for collection in test_collections:
            try:
                qdrant_service.delete_collection(collection)
                results["collections_cleaned"] += 1
                logger.info(f"Emergency cleanup: deleted collection {collection}")
            except Exception as e:
                results["errors"].append(f"Collection {collection}: {str(e)}")
    
    except Exception as e:
        results["errors"].append(f"Collection cleanup failed: {str(e)}")
    
    # Clean up test result files
    try:
        test_results_dir = Path("test_results")
        if test_results_dir.exists():
            import shutil
            shutil.rmtree(test_results_dir)
            results["files_cleaned"] += 1
            logger.info("Emergency cleanup: deleted test_results directory")
    except Exception as e:
        results["errors"].append(f"Test results cleanup failed: {str(e)}")
    
    return results
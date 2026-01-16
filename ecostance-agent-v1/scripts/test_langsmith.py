#!/usr/bin/env python3
"""
Test script for LangSmith tracing functionality.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_langsmith_service():
    """Test the LangSmith service initialization and basic functionality."""
    print("🧪 Testing LangSmith Service...")
    
    try:
        from app.services.langsmith_service import langsmith_service, trace
        
        print(f"  ✓ Service enabled: {langsmith_service.is_enabled()}")
        print(f"  ✓ Project: {langsmith_service.config.project_name}")
        print(f"  ✓ Tracing level: {langsmith_service.config.tracing_level.value}")
        
        # Test trace decorator
        @trace(name="test_function", tags=["test"])
        def test_function(x, y):
            return x + y
        
        result = test_function(2, 3)
        print(f"  ✓ Trace decorator works: {result}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_middleware():
    """Test the LangSmith middleware (disabled for limited tracing)."""
    print("\n🧪 Testing LangSmith Middleware...")
    
    print("  ℹ️ HTTP middleware disabled - tracing limited to embedding, RAG, and agent")
    return True

def test_service_decorators():
    """Test limited service decorators."""
    print("\n🧪 Testing Service Decorators...")
    
    try:
        from app.services.langsmith_service import (
            trace_agent, trace_rag, trace_llm, trace_embedding
        )
        
        @trace_agent
        def mock_agent_function():
            return "agent response"
        
        @trace_rag
        def mock_rag_function():
            return "rag response"
        
        @trace_llm
        def mock_llm_function():
            return "llm response"
        
        @trace_embedding
        def mock_embedding_function():
            return [0.1, 0.2, 0.3]
        
        # Test limited decorators
        mock_agent_function()
        mock_rag_function()
        mock_llm_function()
        mock_embedding_function()
        
        print("  ✓ Limited service decorators work (embedding, RAG, agent, LLM)")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_configuration():
    """Test the LangSmith configuration."""
    print("\n🧪 Testing LangSmith Configuration...")
    
    try:
        from app.config.langsmith_config import (
            langsmith_config, should_trace_services,
            get_rag_tags, get_agent_tags, get_embedding_tags
        )
        
        print(f"  ✓ Config loaded: {langsmith_config.enabled}")
        print(f"  ✓ Service tracing: {should_trace_services()}")
        
        # Test tag generation
        rag_tags = get_rag_tags(tenant_id="test")
        agent_tags = get_agent_tags(user_id="test")
        embedding_tags = get_embedding_tags()
        
        print(f"  ✓ RAG tags: {rag_tags}")
        print(f"  ✓ Agent tags: {agent_tags}")
        print(f"  ✓ Embedding tags: {embedding_tags}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_environment_setup():
    """Test environment variable setup."""
    print("\n🧪 Testing Environment Setup...")
    
    env_vars = [
        "LANGCHAIN_TRACING_V2",
        "LANGCHAIN_API_KEY",
        "LANGCHAIN_PROJECT"
    ]
    
    all_set = True
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask API key for security
            display_value = value if var != "LANGCHAIN_API_KEY" else f"{value[:8]}..."
            print(f"  ✓ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: Not set")
            all_set = False
    
    return all_set

def main():
    """Run all tests."""
    print("🚀 LangSmith Tracing Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Configuration", test_configuration),
        ("LangSmith Service", test_langsmith_service),
        ("Middleware", test_middleware),
        ("Service Decorators", test_service_decorators)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All tests passed! LangSmith tracing is ready to use.")
        print("\nNext steps:")
        print("1. Start your application: uvicorn app.main:app --reload")
        print("2. Make some API calls to generate traces")
        print("3. Check your LangSmith dashboard: https://smith.langchain.com")
    else:
        print(f"\n⚠️ {len(results) - passed} tests failed. Please check the configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()
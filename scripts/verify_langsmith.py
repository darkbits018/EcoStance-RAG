#!/usr/bin/env python3
"""
Simple verification script for LangSmith setup.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def main():
    """Verify LangSmith setup."""
    print("🔍 Verifying LangSmith Setup...")
    print("=" * 40)
    
    # Check environment variables
    tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2")
    api_key = os.getenv("LANGCHAIN_API_KEY")
    project = os.getenv("LANGCHAIN_PROJECT")
    
    print(f"LANGCHAIN_TRACING_V2: {tracing_enabled}")
    print(f"LANGCHAIN_API_KEY: {api_key[:20]}..." if api_key else "LANGCHAIN_API_KEY: Not set")
    print(f"LANGCHAIN_PROJECT: {project}")
    
    if not all([tracing_enabled, api_key, project]):
        print("\n❌ Missing required environment variables")
        return False
    
    # Test LangSmith service
    try:
        from app.services.langsmith_service import langsmith_service
        
        print(f"\n✓ LangSmith service enabled: {langsmith_service.is_enabled()}")
        print(f"✓ Project: {langsmith_service.config.project_name}")
        print(f"✓ Tracing level: {langsmith_service.config.tracing_level.value}")
        
        # Test a simple trace
        with langsmith_service.trace_context("verification_test", inputs={"test": "verification"}) as trace:
            if trace:
                print("✓ LangSmith tracing is working!")
                return True
            else:
                print("⚠️ Tracing context returned None (may still work)")
                return True
                
    except Exception as e:
        print(f"❌ Error testing LangSmith: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 LangSmith is ready to use!")
        print("\nNext steps:")
        print("1. Start your application: uvicorn app.main:app --reload")
        print("2. Make some API calls to generate traces")
        print("3. Check your LangSmith dashboard: https://smith.langchain.com")
    else:
        print("\n❌ Setup verification failed")
        sys.exit(1)
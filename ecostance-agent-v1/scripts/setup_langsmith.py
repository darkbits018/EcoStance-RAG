#!/usr/bin/env python3
"""
Setup script for LangSmith tracing integration.
This script helps configure and test LangSmith tracing for the entire system.
"""

import os
import sys
import subprocess
from pathlib import Path

def activate_venv():
    """Activate the virtual environment."""
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found. Please create one first:")
        print("   python -m venv .venv")
        sys.exit(1)
    
    # Activate venv (Windows)
    if os.name == 'nt':
        activate_script = venv_path / "Scripts" / "activate.bat"
        if activate_script.exists():
            print("✓ Virtual environment found")
            return str(activate_script)
    else:
        # Unix/Linux
        activate_script = venv_path / "bin" / "activate"
        if activate_script.exists():
            print("✓ Virtual environment found")
            return str(activate_script)
    
    print("❌ Could not find activation script in virtual environment")
    sys.exit(1)

def install_dependencies():
    """Install LangSmith and update requirements."""
    print("\n📦 Installing LangSmith dependency...")
    
    try:
        # Install langsmith
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "langsmith"
        ], check=True, capture_output=True, text=True)
        
        print("✓ LangSmith installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install LangSmith: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_env_config():
    """Check if LangSmith environment variables are configured."""
    print("\n🔧 Checking LangSmith configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    required_vars = [
        "LANGCHAIN_TRACING_V2",
        "LANGCHAIN_API_KEY", 
        "LANGCHAIN_PROJECT"
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\nPlease add these to your .env file:")
        print("LANGCHAIN_TRACING_V2=true")
        print("LANGCHAIN_API_KEY=your-langsmith-api-key-here")
        print("LANGCHAIN_PROJECT=ecostance-agent-v1")
        return False
    
    print("✓ LangSmith environment variables configured")
    return True

def test_langsmith_connection():
    """Test LangSmith connection."""
    print("\n🧪 Testing LangSmith connection...")
    
    try:
        # Add current directory to Python path
        import sys
        sys.path.insert(0, os.getcwd())
        
        from app.services.langsmith_service import langsmith_service
        
        if langsmith_service.is_enabled():
            print("✓ LangSmith service initialized successfully")
            
            # Test creating a simple trace
            with langsmith_service.trace_context("test_trace", inputs={"test": "setup"}) as trace:
                if trace:
                    print("✓ LangSmith tracing is working")
                    return True
                else:
                    print("⚠️ LangSmith tracing context returned None")
                    return False
        else:
            print("❌ LangSmith service is disabled")
            return False
            
    except Exception as e:
        print(f"❌ LangSmith connection test failed: {e}")
        return False

def show_usage_instructions():
    """Show instructions for using LangSmith tracing."""
    print("\n📋 LangSmith Tracing Setup Complete!")
    print("\n🎯 What's been configured:")
    print("  • LangSmith dependency installed")
    print("  • Tracing middleware added to FastAPI")
    print("  • Core services instrumented with tracing:")
    print("    - Embedding service (@trace_embedding)")
    print("    - Qdrant service (@trace_database)")
    print("    - RAG query service (@trace_rag)")
    print("    - QuickShip agent (@trace_agent)")
    print("    - LLM calls (@trace_llm)")
    print("    - HTTP requests (middleware)")
    
    print("\n🔧 To get started:")
    print("  1. Get your LangSmith API key from: https://smith.langchain.com")
    print("  2. Update LANGCHAIN_API_KEY in your .env file")
    print("  3. Set LANGCHAIN_TRACING_V2=true in your .env file")
    print("  4. Start your application: uvicorn app.main:app --reload")
    
    print("\n📊 What you'll see in LangSmith:")
    print("  • HTTP request traces with timing and status")
    print("  • RAG query execution with retrieval and generation steps")
    print("  • Agent conversations with tool usage")
    print("  • LLM calls with input/output tokens and latency")
    print("  • Database operations and embedding generation")
    
    print("\n🔍 Debugging features:")
    print("  • Each HTTP request gets a trace ID in X-Trace-ID header")
    print("  • Errors are automatically captured in traces")
    print("  • User and tenant context included in traces")
    print("  • Performance metrics for all operations")

def main():
    """Main setup function."""
    print("🚀 Setting up LangSmith tracing for EcoStance Agent V1")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("app").exists() or not Path("requirements.txt").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check environment configuration
    if not check_env_config():
        print("\n⚠️ Environment configuration incomplete.")
        print("Please update your .env file and run this script again.")
        sys.exit(1)
    
    # Test connection
    if not test_langsmith_connection():
        print("\n⚠️ LangSmith connection test failed.")
        print("Please check your API key and try again.")
        sys.exit(1)
    
    # Show usage instructions
    show_usage_instructions()
    
    print("\n✅ LangSmith tracing setup complete!")
    print("Start your application to begin tracing.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test script for LLM provider switching functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from quickship_agent.agent_service import AgentService
from quickship_agent.llm_factory import LLMFactory
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_llm_providers():
    """Test different LLM providers"""
    print("🧪 Testing LLM Provider Switching\n")
    
    # Check available providers
    providers = LLMFactory.get_available_providers()
    print("📋 Available Providers:")
    for provider, info in providers.items():
        status = "✅ Available" if info["available"] else "❌ Not configured"
        print(f"  {provider}: {status}")
        if info["available"]:
            print(f"    Models: {', '.join(info['models'][:3])}...")
    print()
    
    # Test each available provider
    test_message = "Hello! What can you help me with?"
    session_id = "test_session"
    
    for provider, info in providers.items():
        if not info["available"]:
            print(f"⏭️  Skipping {provider} (not configured)")
            continue
            
        print(f"🔄 Testing {provider.upper()} provider...")
        
        try:
            # Create agent with specific provider
            agent = AgentService(llm_provider=provider)
            
            # Get current LLM info
            llm_info = agent.get_current_llm_info()
            print(f"   Provider: {llm_info['provider']}")
            print(f"   Model: {llm_info['model']}")
            print(f"   Temperature: {llm_info['temperature']}")
            
            # Test a simple chat
            print(f"   Testing with message: '{test_message}'")
            response = agent.chat(session_id, test_message)
            
            if response["success"]:
                print(f"   ✅ Response: {response['response'][:100]}...")
            else:
                print(f"   ❌ Error: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Failed to test {provider}: {e}")
        
        print()
    
    # Test provider switching
    print("🔄 Testing Provider Switching...")
    
    try:
        agent = AgentService()
        initial_info = agent.get_current_llm_info()
        print(f"   Initial provider: {initial_info['provider']}")
        
        # Try to switch to a different provider
        available_providers = [p for p, info in providers.items() if info["available"]]
        if len(available_providers) > 1:
            target_provider = [p for p in available_providers if p != initial_info['provider']][0]
            print(f"   Switching to: {target_provider}")
            
            switch_result = agent.switch_llm_provider(target_provider)
            if switch_result["success"]:
                print(f"   ✅ {switch_result['message']}")
                
                # Test the switched provider
                response = agent.chat(session_id + "_switched", test_message)
                if response["success"]:
                    print(f"   ✅ Switched provider works: {response['response'][:50]}...")
                else:
                    print(f"   ❌ Switched provider failed: {response.get('error')}")
            else:
                print(f"   ❌ Switch failed: {switch_result['message']}")
        else:
            print("   ⏭️  Only one provider available, skipping switch test")
            
    except Exception as e:
        print(f"   ❌ Provider switching test failed: {e}")
    
    print("\n🎉 LLM Provider Testing Complete!")


if __name__ == "__main__":
    test_llm_providers()
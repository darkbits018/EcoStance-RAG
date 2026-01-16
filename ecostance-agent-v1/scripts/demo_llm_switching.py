#!/usr/bin/env python3
"""
Demo script showing LLM provider switching functionality
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


def demo_llm_switching():
    """Demo LLM provider switching"""
    print("🚀 LLM Provider Switching Demo\n")
    
    # Check available providers
    providers = LLMFactory.get_available_providers()
    print("📋 Available Providers:")
    for provider, info in providers.items():
        status = "✅ Available" if info["available"] else "❌ Not configured"
        print(f"  {provider}: {status}")
        if info["available"]:
            print(f"    Sample models: {', '.join(info['models'][:2])}...")
    print()
    
    # Create agent with default provider
    print("🤖 Creating agent with default provider...")
    agent = AgentService()
    
    # Get current LLM info
    llm_info = agent.get_current_llm_info()
    print(f"   Current provider: {llm_info['provider']}")
    print(f"   Current model: {llm_info['model']}")
    print()
    
    # Test a simple message
    test_message = "What is QuickShip?"
    session_id = "demo_session"
    
    print(f"💬 Testing with message: '{test_message}'")
    response = agent.chat(session_id, test_message)
    
    if response["success"]:
        print(f"   ✅ Response: {response['response'][:100]}...")
    else:
        print(f"   ❌ Error: {response.get('error', 'Unknown error')}")
    print()
    
    # Try switching providers if multiple are available
    available_providers = [p for p, info in providers.items() if info["available"]]
    
    if len(available_providers) > 1:
        # Switch to a different provider
        current_provider = llm_info['provider']
        target_provider = [p for p in available_providers if p != current_provider][0]
        target_model = providers[target_provider]['models'][0]  # Use first available model
        
        print(f"🔄 Switching from {current_provider} to {target_provider}...")
        print(f"   Target model: {target_model}")
        
        switch_result = agent.switch_llm_provider(target_provider, target_model)
        
        if switch_result["success"]:
            print(f"   ✅ {switch_result['message']}")
            
            # Test the switched provider
            print(f"💬 Testing switched provider with: '{test_message}'")
            response = agent.chat(session_id + "_switched", test_message)
            
            if response["success"]:
                print(f"   ✅ Response: {response['response'][:100]}...")
            else:
                print(f"   ❌ Error: {response.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Switch failed: {switch_result['message']}")
    else:
        print("⏭️  Only one provider available, skipping switch demo")
        if len(available_providers) == 0:
            print("   No providers are configured with valid API keys")
        else:
            print(f"   Available provider: {available_providers[0]}")
    
    print("\n🎯 Demo Complete!")
    print("\nTo enable Groq:")
    print("1. Get a Groq API key from https://console.groq.com/")
    print("2. Set GROQ_API_KEY in your .env file")
    print("3. Run this demo again to see provider switching in action!")


if __name__ == "__main__":
    demo_llm_switching()
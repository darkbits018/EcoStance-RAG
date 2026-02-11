"""
Test script for EcoStance Agent
"""
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.ecostance_agent.service import EcoStanceAgentService

def test_ecostance_agent():
    print("🌿 Testing EcoStance Agent\n")
    print("=" * 60)
    
    # Initialize agent
    agent = EcoStanceAgentService(tenant_id="test-tenant")
    session_id = "eco-test-123"
    
    # Test 1: Certificate Tracking
    print("\n1. Testing Certificate Tracking:")
    print("-" * 60)
    response = agent.chat(session_id, "Track my certificate CERT-12345")
    print(json.dumps(response, indent=2))
    
    # Test 2: Eco Shopping
    print("\n2. Testing Eco Shopping:")
    print("-" * 60)
    response = agent.chat(session_id, "Show me some eco-friendly solar products")
    print(json.dumps(response, indent=2))
    
    # Test 3: Impact Summary
    print("\n3. Testing Impact Summary:")
    print("-" * 60)
    response = agent.chat(session_id, "What is my total environmental impact?")
    print(json.dumps(response, indent=2))
    
    # Test 4: General Chat
    print("\n4. Testing General Chat:")
    print("-" * 60)
    response = agent.chat(session_id, "How can you help me save the planet?")
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    test_ecostance_agent()

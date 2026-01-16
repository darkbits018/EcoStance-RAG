/**
 * Test script for AI Agent Beta API integration
 * 
 * This script tests the AI Agent Beta endpoints to ensure they're working correctly.
 * Run this after starting your backend server.
 */

import { agentAPI } from './services/api';

async function testAIAgentBeta() {
  console.log('🧪 Testing AI Agent Beta Integration\n');

  try {
    // Test 1: Simple chat message
    console.log('Test 1: Sending a simple chat message...');
    const response1 = await agentAPI.chat('Hello, who are you?');
    console.log('✅ Response:', response1);
    console.log('Session ID:', (response1 as any).session_id);
    console.log('');

    // Test 2: Chat with session ID
    const sessionId = (response1 as any).session_id;
    console.log('Test 2: Sending follow-up message with session ID...');
    const response2 = await agentAPI.chat('What can you help me with?', sessionId);
    console.log('✅ Response:', response2);
    console.log('');

    // Test 3: Get conversation history
    console.log('Test 3: Fetching conversation history...');
    const history = await agentAPI.getHistory(sessionId);
    console.log('✅ History:', history);
    console.log('Message count:', (history as any).message_count);
    console.log('');

    // Test 4: Track shipment
    console.log('Test 4: Testing shipment tracking...');
    const response3 = await agentAPI.chat('Track shipment QS250001', sessionId);
    console.log('✅ Response:', response3);
    console.log('');

    // Test 5: Reset conversation
    console.log('Test 5: Resetting conversation...');
    const resetResponse = await agentAPI.reset(sessionId);
    console.log('✅ Reset response:', resetResponse);
    console.log('');

    console.log('✅ All tests passed!');
  } catch (error) {
    console.error('❌ Test failed:', error);
    if (error instanceof Error) {
      console.error('Error message:', error.message);
    }
  }
}

// Run tests if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  testAIAgentBeta();
}

export { testAIAgentBeta };

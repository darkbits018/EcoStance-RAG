import { useState, useCallback } from 'react';
import { agentAPI } from '../services/api';
import type { AgentChatResponse, AgentHistoryResponse, AgentHistoryMessage } from '../services/api.types';

export const useAIAgent = (knowledgeBase?: string, databaseConnection?: string) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<AgentHistoryMessage[]>([]);

  const chat = useCallback(async (message: string): Promise<AgentChatResponse | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await agentAPI.chat(
        message, 
        sessionId || undefined,
        knowledgeBase,
        databaseConnection
      ) as AgentChatResponse;
      
      // Update session ID if new
      if (response.session_id && response.session_id !== sessionId) {
        setSessionId(response.session_id);
      }
      
      // Add messages to local state
      setMessages(prev => [
        ...prev,
        { role: 'user', content: message, timestamp: response.timestamp },
        { role: 'assistant', content: response.response, timestamp: response.timestamp },
      ]);
      
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, [sessionId, knowledgeBase, databaseConnection]);

  const getHistory = useCallback(async (sid?: string): Promise<AgentHistoryResponse | null> => {
    const targetSessionId = sid || sessionId;
    if (!targetSessionId) {
      setError('No session ID available');
      return null;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await agentAPI.getHistory(targetSessionId) as AgentHistoryResponse;
      setMessages(response.messages);
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch history';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const reset = useCallback(async (sid?: string): Promise<boolean> => {
    const targetSessionId = sid || sessionId;
    if (!targetSessionId) {
      setError('No session ID available');
      return false;
    }

    setLoading(true);
    setError(null);
    
    try {
      await agentAPI.reset(targetSessionId);
      setMessages([]);
      setSessionId(null);
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to reset conversation';
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setError(null);
  }, []);

  return {
    chat,
    getHistory,
    reset,
    clearMessages,
    loading,
    error,
    sessionId,
    messages,
  };
};

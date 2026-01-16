import React, { useState, useEffect } from 'react';
import { MessageList } from '../components/chat/MessageList';
import { ChatInput } from '../components/chat/ChatInput';
import { Message } from '../components/chat/MessageBubble';
import { Icons } from '../components/icons';
import { Button } from '../components/ui/Button';
import { publicAgentAPI } from '../services/api';

interface PublicAgentConfig {
  enabled: boolean;
  allowed_kbs: string[];
  allowed_dbs: string[];
  welcome_message: string;
  suggested_questions: string[];
  branding: {
    logo_url?: string;
    primary_color: string;
    company_name: string;
  };
  rate_limit: {
    queries_per_minute: number;
    max_messages_per_session: number;
  };
  features: {
    show_sources: boolean;
    allow_feedback: boolean;
    show_suggested_questions: boolean;
    enable_database_tools: boolean;
    enable_knowledge_base: boolean;
  };
}

const PublicAgentPage: React.FC = () => {
  const [config, setConfig] = useState<PublicAgentConfig | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingConfig, setIsLoadingConfig] = useState(true);
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  const [messageCount, setMessageCount] = useState(0);
  const [lastQueryTime, setLastQueryTime] = useState(0);
  const [queriesInLastMinute, setQueriesInLastMinute] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadConfig = async () => {
      try {
        const data = await publicAgentAPI.getConfig() as PublicAgentConfig;
        setConfig(data);
        
        if (data.enabled && data.welcome_message) {
          const welcomeMessage: Message = {
            id: 'welcome',
            role: 'assistant',
            content: data.welcome_message,
            timestamp: new Date(),
          };
          setMessages([welcomeMessage]);
        }
      } catch (err) {
        console.error('Error loading config:', err);
        setError('Failed to load AI agent configuration');
      } finally {
        setIsLoadingConfig(false);
      }
    };

    loadConfig();
  }, []);

  const checkRateLimit = (): boolean => {
    if (!config) return false;
    
    const now = Date.now();
    const oneMinuteAgo = now - 60000;
    
    if (lastQueryTime < oneMinuteAgo) {
      setQueriesInLastMinute(0);
    }
    
    if (queriesInLastMinute >= config.rate_limit.queries_per_minute) {
      return false;
    }
    
    if (messageCount >= config.rate_limit.max_messages_per_session) {
      return false;
    }
    
    return true;
  };

  const handleSendMessage = async (content: string) => {
    if (!config) return;
    
    if (!checkRateLimit()) {
      const errorMessage: Message = {
        id: `msg-${Date.now()}-rate-limit`,
        role: 'assistant',
        content: 'Sorry, you\'ve reached the maximum number of questions. Please wait a moment before asking again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      return;
    }

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setMessageCount(prev => prev + 1);
    setQueriesInLastMinute(prev => prev + 1);
    setLastQueryTime(Date.now());

    setIsLoading(true);
    try {
      const conversationHistory = messages
        .filter(m => m.role === 'user' || m.role === 'assistant')
        .map(m => ({
          role: m.role,
          content: m.content,
        }));

      const response = await publicAgentAPI.chat({
        session_id: sessionId,
        message: content,
        conversation_history: conversationHistory,
      }) as any;

      const assistantMessage: Message = {
        id: response.message_id || `msg-${Date.now()}-response`,
        role: 'assistant',
        content: response.response || response.answer,
        timestamp: new Date(response.timestamp),
        sources: config.features.show_sources && response.sources ? response.sources.map((src: any) => ({
          filename: src.filename || src.source,
          chunkNumber: src.chunk_number,
          similarity: src.similarity || src.score,
          preview: src.preview || src.content,
        })) : undefined,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error('Error querying public agent:', error);
      const errorMessage: Message = {
        id: `msg-${Date.now()}-error`,
        role: 'assistant',
        content: error.message || 'Sorry, I\'m having trouble processing your request right now. Please try again in a moment.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    handleSendMessage(question);
  };

  const handleNewConversation = () => {
    if (!config) return;
    setMessages([{
      id: 'welcome-new',
      role: 'assistant',
      content: config.welcome_message,
      timestamp: new Date(),
    }]);
    setMessageCount(0);
  };

  const handleCopyMessage = (messageId: string) => {
    console.log('Copied message:', messageId);
  };

  const handleFeedback = async (messageId: string, type: 'positive' | 'negative') => {
    try {
      await publicAgentAPI.submitFeedback({
        session_id: sessionId,
        message_id: messageId,
        feedback_type: type,
      });
      console.log('Feedback submitted:', messageId, type);
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  if (isLoadingConfig) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <Icons.Spinner className="h-8 w-8 text-primary mx-auto mb-4 animate-spin" />
          <p className="text-text-secondary">Loading AI assistant...</p>
        </div>
      </div>
    );
  }

  if (error || !config) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <Icons.Brain className="h-16 w-16 text-text-secondary mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-text mb-2">AI Assistant Unavailable</h2>
          <p className="text-text-secondary">{error || 'Failed to load AI assistant configuration'}</p>
        </div>
      </div>
    );
  }

  if (!config.enabled) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <Icons.Brain className="h-16 w-16 text-text-secondary mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-text mb-2">AI Assistant Unavailable</h2>
          <p className="text-text-secondary">The AI assistant service is currently disabled.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <div 
        className="bg-surface border-b border-border px-6 py-4 shadow-sm"
        style={{ borderBottomColor: config.branding.primary_color + '20' }}
      >
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {config.branding.logo_url ? (
              <img 
                src={config.branding.logo_url} 
                alt={config.branding.company_name}
                className="h-8 w-auto"
              />
            ) : (
              <div 
                className="h-8 w-8 rounded flex items-center justify-center text-white font-bold text-sm"
                style={{ backgroundColor: config.branding.primary_color }}
              >
                {config.branding.company_name.charAt(0)}
              </div>
            )}
            <div>
              <h1 className="text-xl font-semibold text-text flex items-center gap-2">
                {config.branding.company_name} AI Assistant
                <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full font-normal">BETA</span>
              </h1>
              <p className="text-sm text-text-secondary">
                {config.features.enable_database_tools && config.features.enable_knowledge_base 
                  ? 'Ask questions about data or documents'
                  : config.features.enable_database_tools 
                  ? 'Ask questions about your data'
                  : 'Get instant help'}
              </p>
            </div>
          </div>
          <Button
            variant="outline"
            onClick={handleNewConversation}
            size="sm"
          >
            <Icons.Plus className="h-4 w-4 mr-2" />
            New Chat
          </Button>
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 flex justify-center overflow-hidden">
        <div className="w-full max-w-4xl flex flex-col mx-4 my-6">
          <div className="flex-1 bg-surface rounded-lg shadow-lg border border-border flex flex-col overflow-hidden">
            <div className="flex-1 overflow-y-auto">
              <MessageList
                messages={messages}
                isLoading={isLoading}
                onCopyMessage={config.features.allow_feedback ? handleCopyMessage : undefined}
                onFeedback={config.features.allow_feedback ? handleFeedback : undefined}
              />

              {/* Suggested Questions */}
              {config.features.show_suggested_questions && messages.length <= 1 && config.suggested_questions.length > 0 && (
                <div className="px-4 pb-4">
                  <p className="text-sm font-medium text-text mb-3">Suggested questions:</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {config.suggested_questions.map((question, index) => (
                      <button
                        key={index}
                        onClick={() => handleSuggestedQuestion(question)}
                        className="text-left p-3 text-sm text-text bg-background hover:bg-surface-hover rounded-lg border border-border transition-colors"
                        disabled={isLoading}
                      >
                        {question}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="border-t border-border">
              <ChatInput
                onSend={handleSendMessage}
                disabled={isLoading}
                placeholder="Ask me anything..."
              />
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-surface border-t border-border px-6 py-3">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-xs text-text-secondary">
            Powered by {config.branding.company_name} AI • 
            {messageCount}/{config.rate_limit.max_messages_per_session} messages used
          </p>
        </div>
      </div>
    </div>
  );
};

export default PublicAgentPage;

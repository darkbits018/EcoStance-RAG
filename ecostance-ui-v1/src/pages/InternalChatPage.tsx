import React, { useState, useEffect } from 'react';
import { Button } from '../components/ui/Button';
import { Icons } from '../components/icons';
import { MessageList } from '../components/chat/MessageList';
import { ChatInput } from '../components/chat/ChatInput';
import { KBSelector, KnowledgeBase } from '../components/chat/KBSelector';
import { Message } from '../components/chat/MessageBubble';
import { Badge } from '../components/ui/Badge';
import { useKnowledgeBase } from '../hooks/useKnowledgeBase';
import { knowledgeBaseAPI } from '../services/api';

const InternalChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedKBs, setSelectedKBs] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showKBSelector, setShowKBSelector] = useState(false);
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  
  const { listKnowledgeBases, queryKB } = useKnowledgeBase();

  // Fetch knowledge bases on mount
  useEffect(() => {
    const fetchKBs = async () => {
      try {
        const response = await listKnowledgeBases();
        console.log('KB API Response:', response); // Debug log
        
        if (response && Array.isArray(response)) {
          const transformedKBs: KnowledgeBase[] = response.map((kb: any) => {
            // Handle both string array and object array formats
            if (typeof kb === 'string') {
              return {
                id: kb,
                name: kb,
                documentCount: 0,
                status: 'Ready' as const,
              };
            }
            return {
              id: kb.name || kb.id,
              name: kb.name || kb.id,
              documentCount: kb.document_count || kb.documentCount || 0,
              status: 'Ready' as const,
            };
          });
          console.log('Transformed KBs:', transformedKBs); // Debug log
          setKnowledgeBases(transformedKBs);
        }
      } catch (error) {
        console.error('Failed to fetch knowledge bases:', error);
      }
    };
    fetchKBs();
  }, [listKnowledgeBases]);

  // Query knowledge bases using real API
  const handleSendMessage = async (content: string) => {
    if (selectedKBs.length === 0) {
      alert('Please select at least one knowledge base');
      return;
    }

    // Add user message
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Query the knowledge bases using real API
    setIsLoading(true);
    try {
      // Query the first selected KB (you can enhance this to query multiple KBs)
      const kbName = selectedKBs[0];
      const chatHistory = messages.map(m => `${m.role}: ${m.content}`);
      
      const response = await queryKB(kbName, content, chatHistory);
      
      if (response) {
        const assistantMessage: Message = {
          id: `msg-${Date.now()}-response`,
          role: 'assistant',
          content: response.answer || response.response || 'No answer found.',
          timestamp: new Date(),
          sources: response.sources?.map((source: any, index: number) => ({
            filename: source.metadata?.filename || source.filename || `source-${index}`,
            chunkNumber: source.metadata?.chunk_number || index,
            pageNumber: source.metadata?.page_number,
            similarity: source.score || source.similarity || 0,
            preview: source.text || source.content || '',
          })),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('Error querying KB:', error);
      // Add error message
      const errorMessage: Message = {
        id: `msg-${Date.now()}-error`,
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewConversation = () => {
    if (messages.length > 0) {
      const confirmed = window.confirm(
        'Are you sure you want to start a new conversation? Current messages will be cleared.'
      );
      if (confirmed) {
        setMessages([]);
      }
    }
  };

  const handleCopyMessage = (messageId: string) => {
    console.log('Copied message:', messageId);
  };

  const handleFeedback = (messageId: string, type: 'positive' | 'negative') => {
    console.log('Feedback:', messageId, type);
  };

  const selectedKBNames = knowledgeBases
    .filter((kb) => selectedKBs.includes(kb.id))
    .map((kb) => kb.name);

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <div className="bg-surface border-b border-border px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text">Internal Chat</h1>
            <p className="text-sm text-text-secondary mt-1">
              Query knowledge bases with AI assistance
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              onClick={handleNewConversation}
              disabled={messages.length === 0}
            >
              <Icons.Plus className="h-4 w-4 mr-2" />
              New Chat
            </Button>
          </div>
        </div>

        {/* KB Selection Bar */}
        <div className="mt-4 flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={() => setShowKBSelector(!showKBSelector)}
            className="flex items-center space-x-2"
          >
            <Icons.Database className="h-4 w-4" />
            <span>
              {selectedKBs.length === 0
                ? 'Select Knowledge Bases'
                : `${selectedKBs.length} KB${selectedKBs.length > 1 ? 's' : ''} Selected`}
            </span>
            <Icons.ChevronDown className="h-4 w-4" />
          </Button>

          {selectedKBs.length > 0 && (
            <div className="flex items-center space-x-2 flex-wrap">
              {selectedKBNames.map((name, index) => (
                <Badge key={index} variant="default" className="text-xs">
                  {name}
                </Badge>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* KB Selector Modal */}
      {showKBSelector && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <KBSelector
            knowledgeBases={knowledgeBases}
            selectedKBs={selectedKBs}
            onSelectionChange={setSelectedKBs}
            onClose={() => setShowKBSelector(false)}
          />
        </div>
      )}

      {/* Chat Area */}
      <div className="flex-1 flex flex-col bg-surface max-w-5xl mx-auto w-full border-x border-border">
        {/* Messages */}
        <MessageList
          messages={messages}
          isLoading={isLoading}
          onCopyMessage={handleCopyMessage}
          onFeedback={handleFeedback}
        />

        {/* Input */}
        <ChatInput
          onSend={handleSendMessage}
          disabled={isLoading || selectedKBs.length === 0}
          placeholder={
            selectedKBs.length === 0
              ? 'Select a knowledge base to start chatting...'
              : 'Ask a question...'
          }
        />
      </div>
    </div>
  );
};

export default InternalChatPage;

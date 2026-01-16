import React, { useEffect, useRef } from 'react';
import { MessageBubble, Message } from './MessageBubble';

interface MessageListProps {
    messages: Message[];
    isLoading?: boolean;
    onCopyMessage?: (messageId: string) => void;
    onFeedback?: (messageId: string, type: 'positive' | 'negative') => void;
}

export const MessageList: React.FC<MessageListProps> = ({
    messages,
    isLoading = false,
    onCopyMessage,
    onFeedback,
}) => {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading]);

    return (
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-background">
            {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                    <div className="text-text-secondary mb-4">
                        <Icons.MessageSquare className="h-16 w-16 mx-auto mb-4" />
                    </div>
                    <h3 className="text-lg font-semibold text-text mb-2">
                        No messages yet
                    </h3>
                    <p className="text-sm text-text-secondary max-w-md">
                        Select a knowledge base and ask a question to get started
                    </p>
                </div>
            ) : (
                <>
                    {messages.map((message) => (
                        <MessageBubble
                            key={message.id}
                            message={message}
                            onCopy={() => onCopyMessage?.(message.id)}
                            onFeedback={(type) => onFeedback?.(message.id, type)}
                        />
                    ))}

                    {isLoading && (
                        <div className="flex justify-start mb-4">
                            <div className="max-w-[80%] bg-surface border border-border rounded-lg px-4 py-3">
                                <div className="flex items-center space-x-2">
                                    <div className="flex space-x-1">
                                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                    </div>
                                    <span className="text-sm text-text-secondary">Thinking...</span>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </>
            )}
        </div>
    );
};

// Import Icons for empty state
import { Icons } from '../icons';

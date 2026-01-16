import React from 'react';
import { Icons } from '../icons';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';

export interface Source {
  filename: string;
  chunkNumber: number;
  pageNumber?: number;
  similarity?: number;
  preview?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
}

interface MessageBubbleProps {
  message: Message;
  onCopy?: () => void;
  onFeedback?: (type: 'positive' | 'negative') => void;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  onCopy,
  onFeedback,
}) => {
  const [showSources, setShowSources] = React.useState(false);
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    onCopy?.();
  };

  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Message bubble */}
        <div
          className={`rounded-lg px-4 py-3 ${
            isUser
              ? 'bg-primary text-white'
              : 'bg-surface border border-border text-text'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* Timestamp */}
        <div className={`text-xs text-text-secondary mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>

        {/* Assistant message actions */}
        {!isUser && (
          <div className="mt-2 flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              className="h-8 px-2"
            >
              {copied ? (
                <>
                  <Icons.Check className="h-3 w-3 mr-1" />
                  <span className="text-xs">Copied</span>
                </>
              ) : (
                <>
                  <Icons.FileText className="h-3 w-3 mr-1" />
                  <span className="text-xs">Copy</span>
                </>
              )}
            </Button>

            {onFeedback && (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onFeedback('positive')}
                  className="h-8 px-2"
                >
                  <span className="text-xs">👍</span>
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onFeedback('negative')}
                  className="h-8 px-2"
                >
                  <span className="text-xs">👎</span>
                </Button>
              </>
            )}

            {message.sources && message.sources.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSources(!showSources)}
                className="h-8 px-2"
              >
                <Icons.FileText className="h-3 w-3 mr-1" />
                <span className="text-xs">
                  {message.sources.length} Source{message.sources.length > 1 ? 's' : ''}
                </span>
                {showSources ? (
                  <Icons.ChevronUp className="h-3 w-3 ml-1" />
                ) : (
                  <Icons.ChevronDown className="h-3 w-3 ml-1" />
                )}
              </Button>
            )}
          </div>
        )}

        {/* Sources */}
        {!isUser && showSources && message.sources && message.sources.length > 0 && (
          <div className="mt-3 space-y-2">
            <p className="text-xs font-semibold text-text">Sources:</p>
            {message.sources.map((source, index) => (
              <div
                key={index}
                className="bg-background border border-border rounded p-2 text-xs"
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center space-x-2">
                    <Icons.FileText className="h-3 w-3 text-text-secondary" />
                    <span className="font-medium text-text">{source.filename}</span>
                  </div>
                  {source.similarity && (
                    <Badge variant="outline" className="text-xs">
                      {Math.round(source.similarity * 100)}% match
                    </Badge>
                  )}
                </div>
                <div className="text-text-secondary">
                  Chunk {source.chunkNumber}
                  {source.pageNumber && ` • Page ${source.pageNumber}`}
                </div>
                {source.preview && (
                  <div className="mt-2 text-text-secondary italic border-l-2 border-border pl-2">
                    "{source.preview.substring(0, 150)}..."
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

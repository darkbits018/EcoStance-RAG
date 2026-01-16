import React, { useState, useRef, useEffect } from 'react';
import { Button } from '../ui/Button';
import { Icons } from '../icons';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  disabled = false,
  placeholder = 'Ask a question...',
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [message]);

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-border bg-surface p-4">
      <div className="flex items-end space-x-2">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className="w-full resize-none rounded-lg bg-background border border-border text-text placeholder:text-text-secondary px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:bg-surface disabled:cursor-not-allowed"
            style={{ minHeight: '48px', maxHeight: '120px' }}
          />
          <div className="absolute right-2 bottom-2 text-xs text-text-secondary">
            {message.length > 0 && `${message.length} chars`}
          </div>
        </div>
        <Button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          className="h-12 px-4"
        >
          {disabled ? (
            <Icons.Spinner className="h-5 w-5 animate-spin" />
          ) : (
            <Icons.ArrowUp className="h-5 w-5" />
          )}
        </Button>
      </div>
      <div className="mt-2 text-xs text-text-secondary">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  );
};

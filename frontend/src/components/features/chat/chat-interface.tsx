'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Message } from './message';
import { ChatInput } from './chat-input';
import { apiClient } from '@/lib/api/client';
import type { ChatMessage } from '@/types';

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const sessionId = 'demo-session';

  const handleSendMessage = async (content: string) => {
    const userMessage: ChatMessage = {
      session_id: sessionId,
      user_id: 'demo-user',
      content,
      role: 'user',
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await apiClient.sendMessage({
        session_id: sessionId,
        message: content,
      });

      const assistantMessage: ChatMessage = {
        session_id: sessionId,
        user_id: 'demo-user',
        content: response.message,
        role: 'assistant',
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ChatMessage = {
        session_id: sessionId,
        user_id: 'demo-user',
        content: 'Sorry, something went wrong. Please try again.',
        role: 'assistant',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="flex h-[600px] flex-col">
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center text-muted-foreground">
            <p>Start a conversation with your AI marketing assistant</p>
          </div>
        ) : (
          <div className="space-y-2">
            {messages.map((message, index) => (
              <Message key={index} message={message} />
            ))}
          </div>
        )}
        {isLoading && (
          <div className="flex justify-start px-4 py-3">
            <div className="max-w-[80%] rounded-lg bg-muted px-3 py-2">
              <p className="text-sm text-muted-foreground">Thinking...</p>
            </div>
          </div>
        )}
      </div>
      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
    </Card>
  );
}
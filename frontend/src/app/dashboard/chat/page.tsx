'use client';

import { useAuth } from '@/contexts/AuthContext';
import { ChatInterface } from '@/components/features/chat/chat-interface';

export default function DashboardChatPage() {
  const { user } = useAuth();

  return (
    <div className="h-full flex flex-col p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          AI Marketing Assistant
        </h1>
        <p className="text-lg text-gray-600">
          Hello {user?.name || user?.email}! How can I help you with your marketing today?
        </p>
      </div>
      
      <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <ChatInterface />
      </div>
    </div>
  );
}
import { MainLayout } from '@/components/layout/main-layout';
import { ChatInterface } from '@/components/features/chat/chat-interface';

export default function Home() {
  return (
    <MainLayout>
      <div className="container max-w-4xl mx-auto py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            AI Marketing Assistant
          </h1>
          <p className="text-xl text-muted-foreground">
            Your intelligent companion for marketing strategy and content creation
          </p>
        </div>
        <ChatInterface />
      </div>
    </MainLayout>
  );
}
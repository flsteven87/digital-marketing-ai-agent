import { cn } from '@/lib/utils';
import type { ChatMessage } from '@/types';

interface MessageProps {
  message: ChatMessage;
}

export function Message({ message }: MessageProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={cn(
        'flex w-full gap-3 px-4 py-3',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      <div
        className={cn(
          'max-w-[80%] rounded-lg px-3 py-2',
          isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted text-muted-foreground'
        )}
      >
        <p className="text-sm">{message.content}</p>
      </div>
    </div>
  );
}
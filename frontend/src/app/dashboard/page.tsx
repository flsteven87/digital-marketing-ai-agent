'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function DashboardHomePage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to chat page by default
    router.push('/dashboard/chat');
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
    </div>
  );
}
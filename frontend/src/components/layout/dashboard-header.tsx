'use client';

import { User } from '@/types/auth';
import { Menu } from 'lucide-react';

interface DashboardHeaderProps {
  user: User | null;
  onMenuClick: () => void;
}

export function DashboardHeader({ user, onMenuClick }: DashboardHeaderProps) {
  return (
    <div className="relative z-10 flex-shrink-0 flex h-16 bg-white shadow-sm">
      <button
        onClick={onMenuClick}
        className="px-4 border-r border-gray-200 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500 lg:hidden"
      >
        <span className="sr-only">Open sidebar</span>
        <Menu className="h-6 w-6" />
      </button>
      
      <div className="flex-1 px-4 flex justify-between items-center">
        <div className="flex-1">
          <h1 className="text-2xl font-semibold text-gray-900">
            Dashboard
          </h1>
        </div>
        
        <div className="ml-4 flex items-center md:ml-6">
          <div className="flex items-center">
            <span className="text-sm text-gray-700 mr-3">
              {user?.name || user?.email}
            </span>
            <img
              className="h-8 w-8 rounded-full"
              src={user?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(user?.name || user?.email || 'User')}&background=6366f1&color=fff`}
              alt="User avatar"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
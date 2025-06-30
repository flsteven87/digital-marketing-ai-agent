'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { 
  MessageCircle, 
  User,
  X,
  Home
} from 'lucide-react';

interface DashboardSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navigation = [
  { name: 'AI Chat', href: '/dashboard/chat', icon: MessageCircle },
  { name: 'Account Settings', href: '/dashboard/settings', icon: User },
];

export function DashboardSidebar({ isOpen, onClose }: DashboardSidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    onClose();
  };

  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:flex-shrink-0">
        <div className="flex flex-col w-64">
          <div className="flex flex-col flex-grow bg-gray-900 pt-5 pb-4 overflow-y-auto">
            <div className="flex items-center flex-shrink-0 px-4">
              <Home className="h-8 w-8 text-white" />
              <span className="ml-2 text-xl font-semibold text-white">
                AI Marketing
              </span>
            </div>
            <nav className="mt-8 flex-1 flex flex-col divide-y divide-gray-800 overflow-y-auto">
              <div className="px-2 space-y-1">
                {navigation.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={`
                        group flex items-center px-2 py-2 text-sm leading-6 font-medium rounded-md
                        ${isActive
                          ? 'bg-gray-800 text-white'
                          : 'text-gray-300 hover:text-white hover:bg-gray-700'
                        }
                      `}
                    >
                      <item.icon className="mr-4 h-6 w-6 flex-shrink-0" />
                      {item.name}
                    </Link>
                  );
                })}
              </div>
            </nav>
            
            {/* User section */}
            <div className="flex-shrink-0 flex border-t border-gray-800 p-4">
              <div className="flex items-center">
                <div>
                  <img
                    className="inline-block h-9 w-9 rounded-full"
                    src={user?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(user?.name || user?.email || 'User')}&background=6366f1&color=fff`}
                    alt="User avatar"
                  />
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-white">
                    {user?.name || user?.email}
                  </p>
                  <button
                    onClick={handleLogout}
                    className="text-xs text-gray-300 hover:text-white"
                  >
                    Sign out
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile sidebar */}
      <div className={`lg:hidden fixed inset-y-0 left-0 z-30 w-64 bg-gray-900 overflow-y-auto transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex items-center justify-between flex-shrink-0 px-4 py-4">
          <div className="flex items-center">
            <Home className="h-8 w-8 text-white" />
            <span className="ml-2 text-xl font-semibold text-white">
              AI Marketing
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-gray-300 hover:text-white"
          >
            <X className="h-6 w-6" />
          </button>
        </div>
        
        <nav className="mt-4 flex-1 flex flex-col divide-y divide-gray-800 overflow-y-auto">
          <div className="px-2 space-y-1">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={onClose}
                  className={`
                    group flex items-center px-2 py-2 text-sm leading-6 font-medium rounded-md
                    ${isActive
                      ? 'bg-gray-800 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-gray-700'
                    }
                  `}
                >
                  <item.icon className="mr-4 h-6 w-6 flex-shrink-0" />
                  {item.name}
                </Link>
              );
            })}
          </div>
        </nav>
        
        {/* Mobile user section */}
        <div className="flex-shrink-0 flex border-t border-gray-800 p-4">
          <div className="flex items-center">
            <div>
              <img
                className="inline-block h-9 w-9 rounded-full"
                src={user?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(user?.name || user?.email || 'User')}&background=6366f1&color=fff`}
                alt="User avatar"
              />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-white">
                {user?.name || user?.email}
              </p>
              <button
                onClick={handleLogout}
                className="text-xs text-gray-300 hover:text-white"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
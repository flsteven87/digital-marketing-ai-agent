'use client';

import Link from 'next/link';
import { GoogleLoginButton } from '@/components/auth/GoogleLoginButton';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';

export function Header() {
  const { isAuthenticated, user, logout, isLoading } = useAuth();

  return (
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 max-w-screen-2xl items-center">
        <div className="mr-4 hidden md:flex">
          <Link className="mr-4 flex items-center gap-2 lg:mr-6" href="/">
            <div className="h-6 w-6 rounded bg-blue-600" />
            <span className="hidden font-bold lg:inline-block">
              AI Marketing Assistant
            </span>
          </Link>
        </div>
        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <div className="w-full flex-1 md:w-auto md:flex-none">
            {/* Navigation will go here */}
          </div>
          <div className="flex items-center space-x-4">
            {isLoading ? (
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600" />
            ) : isAuthenticated && user ? (
              <div className="flex items-center space-x-3">
                <Link href="/chat">
                  <Button variant="ghost" size="sm">
                    Dashboard
                  </Button>
                </Link>
                <div className="flex items-center space-x-2">
                  {user.avatar_url && (
                    <img
                      src={user.avatar_url}
                      alt={user.name || user.email}
                      className="h-8 w-8 rounded-full"
                    />
                  )}
                  <span className="text-sm font-medium">{user.name || user.email}</span>
                </div>
                <Button onClick={logout} variant="ghost" size="sm">
                  Logout
                </Button>
              </div>
            ) : (
              <GoogleLoginButton variant="outline" size="sm" className="bg-blue-600 text-white hover:bg-blue-700 border-blue-600" />
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
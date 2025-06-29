'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import type { AuthContextType, AuthState } from '@/types/auth';
import { AuthAPI } from '@/lib/api/auth';
import { TokenManager } from '@/lib/utils/token';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  });

  // Initialize auth state on mount
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      const accessToken = TokenManager.getAccessToken();
      
      if (!accessToken) {
        setState(prev => ({ ...prev, isLoading: false }));
        return;
      }

      // Check if token is expired
      if (TokenManager.isTokenExpired(accessToken)) {
        const refreshTokenValue = TokenManager.getRefreshToken();
        if (refreshTokenValue) {
          const success = await refreshToken();
          if (!success) {
            TokenManager.clearTokens();
            setState(prev => ({ ...prev, isLoading: false }));
            return;
          }
        } else {
          TokenManager.clearTokens();
          setState(prev => ({ ...prev, isLoading: false }));
          return;
        }
      }

      // Get current user
      const user = await AuthAPI.getCurrentUser(TokenManager.getAccessToken()!);
      setState({
        user,
        isLoading: false,
        isAuthenticated: true,
      });
    } catch (error) {
      console.error('Auth initialization failed:', error);
      TokenManager.clearTokens();
      setState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const login = async (): Promise<void> => {
    try {
      setState(prev => ({ ...prev, isLoading: true }));
      
      // Get Google OAuth URL
      const { authorization_url } = await AuthAPI.getGoogleAuthUrl();
      
      // Redirect to Google OAuth
      window.location.href = authorization_url;
    } catch (error) {
      console.error('Login failed:', error);
      setState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const logout = (): void => {
    try {
      const accessToken = TokenManager.getAccessToken();
      if (accessToken) {
        AuthAPI.logout(accessToken).catch(console.error);
      }
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      TokenManager.clearTokens();
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
      });
    }
  };

  const refreshToken = async (): Promise<boolean> => {
    try {
      const refreshTokenValue = TokenManager.getRefreshToken();
      if (!refreshTokenValue) {
        return false;
      }

      const tokens = await AuthAPI.refreshToken(refreshTokenValue);
      TokenManager.setTokens(tokens);
      
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  };

  const value: AuthContextType = {
    ...state,
    login,
    logout,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
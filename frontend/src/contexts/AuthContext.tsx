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
      await updateAuthState();
    } catch (error) {
      console.error('Auth initialization failed:', error);
      TokenManager.clearTokens();
      setState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const login = async (): Promise<void> => {
    try {
      setState(prev => ({ ...prev, isLoading: true }));
      
      const response = await AuthAPI.getGoogleAuthUrl();
      
      if (!response.authorization_url) {
        throw new Error('No authorization URL received');
      }
      
      window.location.href = response.authorization_url;
      
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
      // Clear invalid tokens on refresh failure
      TokenManager.clearTokens();
      return false;
    }
  };

  const updateAuthState = async (): Promise<void> => {
    const accessToken = TokenManager.getAccessToken();
    
    // No token or expired token
    if (!accessToken || TokenManager.isTokenExpired(accessToken)) {
      const refreshTokenValue = TokenManager.getRefreshToken();
      if (refreshTokenValue && refreshTokenValue.trim()) {
        const success = await refreshToken();
        if (!success) {
          _setUnauthenticatedState();
          return;
        }
      } else {
        TokenManager.clearTokens();
        _setUnauthenticatedState();
        return;
      }
    }

    // Try to get current user with valid token
    try {
      const currentToken = TokenManager.getAccessToken();
      if (currentToken && !TokenManager.isTokenExpired(currentToken)) {
        console.log('🔍 Calling /me with token:', currentToken?.substring(0, 50) + '...');
        const user = await AuthAPI.getCurrentUser(currentToken);
        console.log('✅ User fetched successfully:', user);
        setState({
          user,
          isLoading: false,
          isAuthenticated: true,
        });
      } else {
        _setUnauthenticatedState();
      }
    } catch (error) {
      console.error('❌ updateAuthState failed:', error);
      TokenManager.clearTokens();
      _setUnauthenticatedState();
    }
  };

  const _setUnauthenticatedState = () => {
    setState({
      user: null,
      isLoading: false,
      isAuthenticated: false,
    });
  };

  const value: AuthContextType = {
    ...state,
    login,
    logout,
    refreshToken,
    updateAuthState,
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
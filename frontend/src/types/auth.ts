export interface User {
  id: string;
  email: string;
  name?: string;
  avatar_url?: string;
  company?: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in?: number;
}

export interface LoginResponse {
  user: User;
  tokens: TokenResponse;
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export interface AuthContextType extends AuthState {
  login: () => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
  updateAuthState: () => Promise<void>;
}

export interface GoogleAuthResponse {
  authorization_url: string;
  state: string;
}
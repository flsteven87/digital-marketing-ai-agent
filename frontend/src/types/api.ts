export interface ChatMessage {
  id?: string;
  session_id: string;
  user_id: string;
  content: string;
  role: 'user' | 'assistant';
  created_at?: string;
}

export interface ChatSession {
  id: string;
  user_id: string;
  title?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  user_id?: string;
}

export interface ChatResponse {
  message: string;
  session_id: string;
  message_id?: string;
  created_at?: string;
}

export interface ApiError {
  detail: string;
  status: number;
}
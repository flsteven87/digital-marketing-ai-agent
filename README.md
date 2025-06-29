# AI Marketing Assistant

A full-stack AI-powered marketing assistant built with FastAPI, Next.js, and LangGraph. Features Google OAuth authentication, real-time chat, and intelligent conversation management.

## 🚀 Features

- **AI-Powered Chat**: LangGraph-based conversational AI with streaming responses
- **Google OAuth**: Secure authentication with JWT token management
- **Real-time Interface**: Modern React frontend with responsive design
- **Database Persistence**: PostgreSQL with Supabase for chat history and user management
- **Session Management**: Intelligent session handling with auto-generated titles
- **Developer Tools**: Background service management to prevent timeouts

## 🏗️ Architecture

### Backend (FastAPI)
- **Python 3.13** with `uv` package manager
- **LangGraph** for AI agent orchestration
- **FastAPI** for high-performance API endpoints
- **Direct PostgreSQL** connection for optimal performance
- **JWT-based authentication** with refresh tokens

### Frontend (Next.js)
- **Next.js 15** with App Router
- **TypeScript** for type safety
- **React Context** for global state management
- **Tailwind CSS** for styling
- **Protected routes** with authentication

### Database (Supabase)
- **PostgreSQL** with Row Level Security
- **OAuth provider integration**
- **Chat session and message persistence**
- **User management with audit logging**

## 🛠️ Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- Supabase account
- Google OAuth credentials

### Environment Setup

1. **Backend Environment** (`backend/.env`):
```env
DATABASE_URL=your_supabase_postgres_url
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback
OPENAI_API_KEY=your_openai_api_key
JWT_SECRET=your_jwt_secret_key
```

2. **Frontend Environment** (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Installation & Development

1. **Clone the repository**:
```bash
git clone <repo-url>
cd digital-marketing-ai-agent
```

2. **Backend Setup**:
```bash
cd backend
uv install
uv run python scripts/oauth_migration.py  # Setup database
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Frontend Setup**:
```bash
cd frontend
npm install
npm run dev  # Runs on port 3000
```

4. **Database Migration**:
```bash
cd backend
uv run python scripts/oauth_migration.py
```

## 📁 Project Structure

```
digital-marketing-ai-agent/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Configuration & middleware
│   │   ├── models/          # Data models
│   │   └── services/        # Business logic
│   │       ├── ai/          # LangGraph agents
│   │       ├── auth/        # Authentication services
│   │       └── database/    # Database operations
│   ├── scripts/             # Database migrations
│   └── pyproject.toml       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router
│   │   ├── components/      # React components
│   │   ├── contexts/        # React contexts
│   │   ├── lib/             # Utilities & API clients
│   │   └── types/           # TypeScript definitions
│   └── package.json         # Node dependencies
└── README.md
```

## 🔧 Development Tools

### Quick Service Management
The project includes background service management to prevent Claude Code timeouts:

```bash
# Start all services in background
source scripts/start-services.sh && start_all

# Individual commands
start_backend    # Backend on port 8000
start_frontend   # Frontend on port 3000
```

### Code Quality
- **Optimized for maintainability**: Eliminated over-processing patterns
- **Clean architecture**: Separation of concerns with service layers
- **Type safety**: Full TypeScript coverage
- **Best practices**: Modern Python and React patterns

## 🔐 Security Features

- **Google OAuth 2.0** with secure state management
- **JWT tokens** with refresh mechanism
- **PostgreSQL Row Level Security** 
- **Input validation** and sanitization
- **CORS configuration** for cross-origin requests

## 🎯 Key Components

### AI Agent (`app/services/ai/`)
- LangGraph-based conversational AI
- Streaming responses for real-time interaction
- Session context management
- Intelligent title generation

### Authentication (`app/services/auth/`)
- Google OAuth integration
- JWT token management
- User session handling
- Direct PostgreSQL connection

### Chat System (`app/api/v1/chat/`)
- Real-time streaming chat
- Message persistence
- Session management
- User context awareness

## 📊 Database Schema

### Core Tables
- **users**: User profiles with OAuth integration
- **oauth_providers**: OAuth provider data storage
- **chat_sessions**: Conversation sessions
- **chat_messages**: Individual messages
- **user_sessions**: Active session tracking

## 🔄 Recent Optimizations

- **Eliminated over-processing**: Simplified service layer logic
- **Centralized serialization**: Reduced code duplication
- **Streamlined error handling**: Better debugging and maintainability
- **Background services**: Prevents development timeouts

## 🚦 Getting Started

1. Set up your environment variables
2. Run the database migration
3. Start the backend service
4. Start the frontend development server
5. Navigate to `http://localhost:3000`
6. Sign in with Google to start chatting!

---

Built with ❤️ using modern web technologies and AI best practices.
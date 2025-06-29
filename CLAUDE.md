# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
AI Marketing Assistant is an AI-powered marketing automation platform for SMEs. It helps businesses automate content generation, social media scheduling, customer interaction, and analytics reporting using OpenAI's GPT-4 and various social media APIs.

## Development Commands

### Environment Setup
```bash
# Use uv for Python environment management (REQUIRED)
uv venv
source .venv/bin/activate  # Linux/Mac

# Install dependencies from pyproject.toml
uv pip sync

# Add new dependencies
uv add fastapi uvicorn  # Add to project dependencies
uv add --dev pytest black  # Add to dev dependencies
```

### Running the Application

**IMPORTANT: Always shut down existing services before starting new ones to avoid port conflicts.**

**Service Management Rule**: Before starting any service, ALWAYS stop any existing instances first:
- Check for running processes on required ports (8000 for backend, 3000 for frontend)
- Use `lsof -i :8000` to check port 8000 usage
- Use `lsof -i :3000` to check port 3000 usage  
- Kill existing processes with `kill -9 <PID>` if needed
- This prevents "Address already in use" errors and ensures clean service startup

#### Backend (FastAPI)
```bash
# Shut down any existing backend service first
# Use Ctrl+C in the terminal or kill the process

# Start development server
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database setup
uv run python scripts/setup_db.py
```

#### Frontend (Next.js)
```bash
# Shut down any existing frontend service first  
# Use Ctrl+C in the terminal or kill the process

# Start development server
cd frontend
npm run dev
# If port 3000 is in use, Next.js will automatically use port 3001
```

#### Full Stack Development
```bash
# Terminal 1: Start backend
cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend && npm run dev
```

#### Service Status Detection

**IMPORTANT: How to know when services are ready**

When starting services, they may appear to "hang" but are actually running successfully. Look for these indicators:

**Backend is ready when you see:**
- `INFO:     Uvicorn running on http://0.0.0.0:8000`
- `✅ Database initialized successfully`
- No new log output for 5+ seconds (service is idle and ready)

**IMPORTANT: Service Startup Behavior**
- Services may appear to "hang" after showing startup messages - this is NORMAL
- Don't wait for the full 120-second timeout unless there are actual errors
- Once you see the "running on" message, the service is ready to accept requests
- You can immediately test API endpoints or proceed with development
- Only wait longer if you see error messages or exceptions

**Frontend is ready when you see:**
- `✓ Ready in XXXXms`  
- `- Local:        http://localhost:3000`
- No new log output for 5+ seconds (service is idle and ready)

**IMPORTANT: Frontend Startup Behavior**
- Next.js may appear to "hang" after compilation - this is NORMAL
- Don't wait for timeouts unless there are actual build errors
- Once you see "Ready in XXXXms", the frontend is serving requests
- You can immediately open the browser or test the application

## Architecture

The project follows a clean FastAPI architecture:
- `app/main.py`: FastAPI application entry point
- `app/api/v1/`: API route handlers
- `app/services/`: Business logic (story generation, image generation)
- `app/models/`: Pydantic models for request/response validation
- `app/db/`: Database models and operations
- `app/utils/`: Helper functions (content filtering, prompts)

## Key Development Rules

1. **Python Environment**: Always use `uv` for package management
2. **Language**: Communicate with developers in Traditional Chinese (繁體中文), but write all code comments and documentation in English
3. **Code Quality**:
   - Follow PEP8 standards
   - Use type hints for all functions
   - Keep files under 500 lines
   - Create Pytest unit tests for all new features
4. **Safety**: Content must be age-appropriate with comprehensive filtering

## Current Implementation Status

The project is in MVP development phase:
- Backend FastAPI structure implemented with uv and Python 3.13
- Supabase PostgreSQL as database
- Core API routes established (auth, chat, content, social, analytics, admin)
- Frontend Next.js structure planned but not yet implemented

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: For GPT-4 access
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `SUPABASE_SERVICE_KEY`: Supabase service role key
- `SECRET_KEY`: Application secret key for JWT
- `REDIS_URL`: Redis connection for Celery
- Social media API keys (FACEBOOK_APP_ID, LINE_CHANNEL_ID, etc.)

## Package Management

This project uses `pyproject.toml` for dependency management with uv. Always use:
- `uv add <package>` to add production dependencies
- `uv add --dev <package>` to add development dependencies
- `uv pip sync` to install all dependencies
- `uv run <command>` to run any Python commands
- Never use requirements.txt
- Never call python directly, always use `uv run python`
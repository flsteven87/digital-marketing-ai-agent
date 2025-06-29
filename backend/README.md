# AI Marketing Assistant - Backend

AI-powered marketing assistant backend built with FastAPI and Python 3.13.

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) - Python package manager
- Redis (for Celery task queue)
- Supabase account

## Setup

1. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create virtual environment and install dependencies:
```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

3. Copy environment variables:
```bash
cp .env.example .env
```

4. Configure your `.env` file with:
   - Supabase credentials
   - OpenAI API key
   - Social media API keys
   - Other required settings

## Development

### Run the development server:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run tests:
```bash
uv run pytest
```

### Code formatting and linting:
```bash
uv run ruff check .
uv run ruff format .
```

### Type checking:
```bash
uv run mypy app
```

## Project Structure

```
backend/
├── app/
│   ├── api/v1/        # API endpoints
│   ├── core/          # Core configuration
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── main.py        # FastAPI application
├── tests/             # Test files
├── pyproject.toml     # Project configuration
└── .env              # Environment variables
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Docker

Build and run with Docker:
```bash
docker build -t ai-marketing-backend .
docker run -p 8000:8000 ai-marketing-backend
```

Or use Docker Compose:
```bash
docker-compose up
```
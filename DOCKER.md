# Docker Setup for AI Marketing Assistant

## Overview

This project uses Docker for development and production environments. The setup includes:

- **Backend**: FastAPI application (Python 3.13)
- **Frontend**: Next.js application (Node 20)
- **Redis**: For caching and session management
- **Nginx**: Reverse proxy for production

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Make (for convenient commands)

### Environment Setup

1. Copy environment variables:
```bash
cp .env.example .env
```

2. Fill in your environment variables in `.env`

### Development

```bash
# Start development environment
make dev

# View logs
make logs

# Stop services
make down
```

The services will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Production

```bash
# Start production environment
make prod

# View production logs
make prod-logs

# Stop production environment
make prod-down
```

## Available Commands

Run `make help` to see all available commands:

- `make dev` - Start development with hot reload
- `make build` - Build all Docker images
- `make test` - Run tests in containers
- `make clean` - Clean up containers and volumes
- `make shell-backend` - Access backend container shell
- `make migrate` - Run database migrations

## Architecture

### Development Environment

- **Hot Reload**: Code changes are reflected immediately
- **Volume Mounts**: Source code is mounted for live editing
- **Debug Mode**: Detailed logging and error messages

### Production Environment

- **Optimized Images**: Multi-stage builds for smaller images
- **Nginx Proxy**: Load balancing and SSL termination
- **Health Checks**: Automatic service health monitoring
- **Resource Limits**: CPU and memory constraints

## Environment Variables

Key environment variables needed:

```bash
# Database (Supabase)
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=...

# Security
SECRET_KEY=...

# OpenAI
OPENAI_API_KEY=sk-...

# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 3000, 8000, 6379 are available
2. **Permission errors**: Ensure Docker daemon is running
3. **Build failures**: Check Dockerfile syntax and dependencies

### Debug Commands

```bash
# Check container status
make ps

# View specific service logs
make logs-backend
make logs-frontend

# Restart specific service
make restart-backend
make restart-frontend

# Access container shell
make shell-backend
make shell-frontend
```

### Reset Database

```bash
# Reset database tables
make reset-db
```

## Performance

### Image Sizes

- Backend: ~200MB (optimized with multi-stage build)
- Frontend: ~150MB (standalone Next.js build)
- Total: ~350MB excluding base images

### Resource Usage

Development:
- CPU: ~1-2 cores
- Memory: ~2-4GB

Production:
- CPU: ~2-3 cores
- Memory: ~3-5GB

## Security

- Non-root users in containers
- Security headers in Nginx
- Rate limiting configured
- Secrets management for production
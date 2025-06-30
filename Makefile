.PHONY: help dev up down logs build test clean prod shell-backend shell-frontend migrate

# Default target
.DEFAULT_GOAL := help

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo '${BLUE}AI Marketing Assistant - Docker Commands${NC}'
	@echo ''
	@echo 'Usage:'
	@echo '  ${GREEN}make${NC} ${YELLOW}<target>${NC}'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  ${GREEN}%-15s${NC} %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev: ## Start development environment with hot reload
	docker-compose up -d
	@echo "${GREEN}✓ Development environment started${NC}"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

up: ## Start all services in background
	docker-compose up -d
	@echo "${GREEN}✓ All services started${NC}"

down: ## Stop all services
	docker-compose down
	@echo "${GREEN}✓ All services stopped${NC}"

logs: ## Show logs from all services
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

build: ## Build all Docker images
	docker-compose build --no-cache
	@echo "${GREEN}✓ All images built${NC}"

build-backend: ## Build backend Docker image
	docker-compose build --no-cache backend
	@echo "${GREEN}✓ Backend image built${NC}"

build-frontend: ## Build frontend Docker image
	docker-compose build --no-cache frontend
	@echo "${GREEN}✓ Frontend image built${NC}"

test: ## Run tests in containers
	docker-compose run --rm backend pytest
	@echo "${GREEN}✓ Tests completed${NC}"

clean: ## Remove all containers, volumes, and images
	docker-compose down -v --rmi all
	@echo "${GREEN}✓ Cleanup completed${NC}"

prod: ## Start production environment
	docker-compose -f docker-compose.prod.yml up -d
	@echo "${GREEN}✓ Production environment started${NC}"

prod-down: ## Stop production environment
	docker-compose -f docker-compose.prod.yml down
	@echo "${GREEN}✓ Production environment stopped${NC}"

prod-logs: ## Show production logs
	docker-compose -f docker-compose.prod.yml logs -f

shell-backend: ## Open shell in backend container
	docker-compose exec backend /bin/bash

shell-frontend: ## Open shell in frontend container
	docker-compose exec frontend /bin/sh

migrate: ## Run database migrations
	docker-compose exec backend python scripts/create_tables.py
	@echo "${GREEN}✓ Database migrations completed${NC}"

reset-db: ## Reset database (drop and recreate tables)
	docker-compose exec backend python scripts/create_tables.py reset
	@echo "${GREEN}✓ Database reset completed${NC}"

ps: ## Show running containers
	docker-compose ps

restart: ## Restart all services
	$(MAKE) down
	$(MAKE) up
	@echo "${GREEN}✓ All services restarted${NC}"

restart-backend: ## Restart backend service
	docker-compose restart backend
	@echo "${GREEN}✓ Backend restarted${NC}"

restart-frontend: ## Restart frontend service
	docker-compose restart frontend
	@echo "${GREEN}✓ Frontend restarted${NC}"

env-example: ## Create .env.example files
	@cp backend/.env backend/.env.example 2>/dev/null || echo "${YELLOW}Backend .env not found${NC}"
	@cp frontend/.env.local frontend/.env.example 2>/dev/null || echo "${YELLOW}Frontend .env.local not found${NC}"
	@echo "${GREEN}✓ .env.example files created${NC}"
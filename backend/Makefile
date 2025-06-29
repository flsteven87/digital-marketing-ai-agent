.PHONY: help install run dev test lint format clean docker-up docker-down migrate

help:
	@echo "Available commands:"
	@echo "  make install      Install dependencies"
	@echo "  make run         Run the application"
	@echo "  make dev         Run in development mode"
	@echo "  make test        Run tests"
	@echo "  make lint        Run linters"
	@echo "  make format      Format code"
	@echo "  make clean       Clean up cache files"
	@echo "  make docker-up   Start Docker containers"
	@echo "  make docker-down Stop Docker containers"
	@echo "  make migrate     Run database migrations"

install:
	uv python install 3.13
	uv sync --python 3.13

run:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	uv run pytest tests/ -v --cov=app --cov-report=html

lint:
	uv run ruff check app/ tests/
	uv run mypy app/ tests/

format:
	uv run ruff format app/ tests/
	uv run ruff check --fix app/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

migrate:
	uv run alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

migrate-rollback:
	uv run alembic downgrade -1

db-reset:
	uv run alembic downgrade base
	uv run alembic upgrade head

celery-worker:
	uv run celery -A app.services.scheduler.celery_app worker --loglevel=info

celery-beat:
	uv run celery -A app.services.scheduler.celery_app beat --loglevel=info

celery-flower:
	uv run celery -A app.services.scheduler.celery_app flower

redis:
	redis-server

env:
	cp .env.example .env
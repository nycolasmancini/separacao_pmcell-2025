.PHONY: help setup dev test clean build deploy docker-up docker-down

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup        - Initial setup (install dependencies)"
	@echo "  make dev          - Start development servers"
	@echo "  make test         - Run all tests"
	@echo "  make test-backend - Run backend tests only"
	@echo "  make test-frontend- Run frontend tests only"
	@echo "  make lint         - Run linters"
	@echo "  make clean        - Clean temporary files"
	@echo "  make build        - Build for production"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make db-migrate   - Apply database migrations"
	@echo "  make db-seed      - Populate database with test data"
	@echo "  make db-seed-clean- Clean and repopulate database"

# Setup
setup:
	@echo "Setting up backend..."
	cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "Setting up frontend..."
	cd frontend && npm install
	@echo "Creating .env file..."
	cp backend/.env.example backend/.env
	@echo "Setup complete!"

# Development
dev:
	@echo "Starting development servers..."
	@make -j 2 dev-backend dev-frontend

dev-backend:
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

# Testing
test:
	@make test-backend
	@make test-frontend

test-backend:
	cd backend && . venv/bin/activate && pytest -v --cov=app --cov-report=term-missing

test-frontend:
	cd frontend && npm test

test-watch:
	cd backend && . venv/bin/activate && pytest-watch

# Linting
lint:
	@make lint-backend
	@make lint-frontend

lint-backend:
	cd backend && . venv/bin/activate && black . && flake8 app/

lint-frontend:
	cd frontend && npm run lint

# Build
build:
	@echo "Building for production..."
	cd frontend && npm run build
	@echo "Build complete!"

# Docker
docker-up:
	docker-compose up -d
	@echo "Containers started!"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	rm -rf frontend/dist
	rm -rf frontend/node_modules/.vite
	@echo "Cleanup complete!"

# Database
db-migrate:
	cd backend && . venv/bin/activate && alembic upgrade head

db-seed:
	cd backend && . venv/bin/activate && python -m app.db.seed

db-seed-clean:
	cd backend && . venv/bin/activate && python -m app.db.seed --clean
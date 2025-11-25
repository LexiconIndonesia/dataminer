.PHONY: help install dev test test-unit test-integration test-cov test-fast test-watch lint format format-check typecheck check clean migrate migrate-down migration db-reset db-seed docker-build docker-up docker-down api-generate schema-generate sqlc-generate regenerate-all pre-commit pre-commit-install pre-commit-run security

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo '$(BLUE)Dataminer - Available Commands:$(NC)'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ''

# Setup and Installation
install: ## Install all dependencies (production + dev)
	@echo "$(BLUE)Installing dependencies with UV...$(NC)"
	uv sync --all-extras

install-prod: ## Install production dependencies only
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	uv sync --no-dev

# Development
dev: ## Run development server with hot reload
	@echo "$(BLUE)Starting development server...$(NC)"
	uv run uvicorn dataminer.api.app:app --host 0.0.0.0 --port 8000 --reload

# Testing
test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	uv run pytest tests/ -v

test-unit: ## Run unit tests only (no external dependencies)
	@echo "$(BLUE)Running unit tests...$(NC)"
	uv run pytest tests/unit/ -v

test-integration: ## Run integration tests only (requires database)
	@echo "$(BLUE)Running integration tests...$(NC)"
	uv run pytest tests/integration/ -v

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	uv run pytest tests/ -v --cov=src/dataminer --cov-report=term-missing --cov-report=html --cov-report=xml

test-fast: ## Run tests without coverage (faster)
	@echo "$(BLUE)Running fast tests...$(NC)"
	uv run pytest tests/ -v --no-cov

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	uv run pytest-watch tests/ -v

# Code Quality
lint: ## Run linter (ruff check)
	@echo "$(BLUE)Running linter...$(NC)"
	uv run ruff check src/ tests/

lint-fix: ## Run linter and fix issues
	@echo "$(BLUE)Running linter with auto-fix...$(NC)"
	uv run ruff check src/ tests/ --fix

format: ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	uv run ruff format src/ tests/

format-check: ## Check code formatting
	@echo "$(BLUE)Checking code formatting...$(NC)"
	uv run ruff format src/ tests/ --check

typecheck: ## Run type checker (mypy)
	@echo "$(BLUE)Running type checker...$(NC)"
	uv run mypy src/

security: ## Run security scan
	@echo "$(BLUE)Running security scan...$(NC)"
	@echo "Note: Install bandit for security scanning: uv add --dev bandit"
	@echo "For now, checking for common issues..."
	uv run ruff check src/ --select S

check: lint typecheck test ## Run all checks (lint, typecheck, test)

# Database
migrate: ## Apply database migrations
	@echo "$(BLUE)Applying database migrations...$(NC)"
	uv run alembic upgrade head

migrate-down: ## Rollback last migration
	@echo "$(BLUE)Rolling back last migration...$(NC)"
	uv run alembic downgrade -1

migration: ## Create new migration (use MSG="description")
	@echo "$(BLUE)Creating new migration...$(NC)"
	@if [ -z "$(MSG)" ]; then \
		echo "Error: MSG is required. Usage: make migration MSG=\"description\""; \
		exit 1; \
	fi
	uv run alembic revision --autogenerate -m "$(MSG)"

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(BLUE)Resetting database...$(NC)"
	@read -p "This will destroy all data. Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		uv run alembic downgrade base; \
		uv run alembic upgrade head; \
		echo "$(GREEN)Database reset complete$(NC)"; \
	else \
		echo "Cancelled"; \
	fi

db-seed: ## Seed database with test data
	@echo "$(BLUE)Seeding database...$(NC)"
	@echo "TODO: Implement database seeding script"

# Docker
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t dataminer:latest .

docker-up: ## Start all services with docker-compose
	@echo "$(BLUE)Starting services...$(NC)"
	docker-compose up -d

docker-down: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose down

docker-logs: ## View docker-compose logs
	docker-compose logs -f

docker-dev: ## Start services in development mode
	@echo "$(BLUE)Starting services in development mode...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Code Generation
api-generate: ## Generate Pydantic models from OpenAPI spec (contract-first)
	@echo "$(BLUE)Generating Pydantic models from OpenAPI spec...$(NC)"
	@if ! uv run python -c "import datamodel_code_generator" 2>/dev/null; then \
		echo "$(RED)Error: datamodel-code-generator is not installed$(NC)"; \
		echo ""; \
		echo "Install it with: $(GREEN)make install$(NC)"; \
		echo "Or manually with: $(GREEN)uv sync$(NC)"; \
		echo ""; \
		exit 1; \
	fi
	@mkdir -p src/dataminer/api/generated
	uv run datamodel-codegen \
		--input openapi.yaml \
		--output src/dataminer/api/generated/models.py \
		--output-model-type pydantic_v2.BaseModel \
		--target-python-version 3.14 \
		--use-standard-collections \
		--use-schema-description \
		--field-constraints \
		--use-default \
		--use-annotated \
		--use-title-as-name \
		--disable-timestamp
	@echo "$(GREEN)Generated models saved to src/dataminer/api/generated/models.py$(NC)"

schema-generate: ## Generate SQL schema from database (requires running PostgreSQL)
	@echo "$(BLUE)Generating SQL schema from database...$(NC)"
	uv run python scripts/generate_schema.py
	@echo "$(GREEN)SQL schema generated in sql/schema/current_schema.sql$(NC)"
	@echo "$(BLUE)Note: Commit the updated schema file after migrations$(NC)"

sqlc-generate: ## Generate type-safe SQL code with SQLC (uses committed schema)
	@echo "$(BLUE)Generating SQLC code...$(NC)"
	sqlc generate
	@echo "$(GREEN)SQLC code generated in src/dataminer/db/queries$(NC)"

regenerate-all: schema-generate sqlc-generate ## Regenerate schema and SQLC code (after migrations)
	@echo "$(GREEN)Schema and SQLC code regenerated$(NC)"

# Maintenance
clean: ## Clean build artifacts and caches
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ htmlcov/ .coverage coverage.xml
	@echo "$(GREEN)Clean complete$(NC)"

clean-all: clean ## Clean everything including venv
	@echo "$(BLUE)Removing virtual environment...$(NC)"
	rm -rf .venv
	@echo "$(GREEN)All clean$(NC)"

# Pre-commit hooks
pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	uv run pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	uv run pre-commit install

pre-commit-run: pre-commit ## Alias for pre-commit

# Info
version: ## Show project version
	@uv run python -c "from dataminer import __version__; print(__version__)"

info: ## Show project information
	@echo "$(BLUE)Project Information:$(NC)"
	@echo "  Name:    dataminer"
	@echo "  Version: $$(make version)"
	@echo "  Python:  $$(uv run python --version)"
	@echo "  UV:      $$(uv --version)"

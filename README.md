# Dataminer Service

A high-performance document extraction service for processing legal documents from various court sources, starting with Indonesian Supreme Court (ID_SC) documents.

## Features

- 🔍 Multi-source document extraction support
- 📄 PDF processing with OCR capabilities
- 🤖 LLM-powered field extraction
- 🔄 Configurable extraction profiles
- 📊 Cost tracking and optimization
- ⚡ Queue-based processing with NATS
- 🎯 High accuracy with confidence scoring

## Tech Stack

- **Python**: 3.14
- **Package Manager**: UV
- **Web Framework**: FastAPI
- **API Design**: Contract-first with OpenAPI
- **Code Generation**: datamodel-code-generator for Pydantic models
- **Database**: PostgreSQL 16+
- **Migrations**: Alembic
- **SQL**: SQLC for type-safe queries
- **Queue**: NATS JetStream
- **Cache**: Redis 7+
- **Testing**: pytest with async support
- **Containerization**: Docker

## Quick Start

### Prerequisites

- Python 3.14+
- [UV package manager](https://github.com/astral-sh/uv) - Fast Python package installer
- Docker and Docker Compose
- Make

### Installation

```bash
# 1. Install all dependencies (including dev dependencies like datamodel-code-generator)
make install

# 2. Generate API models from OpenAPI spec
#    This requires datamodel-code-generator to be installed (included in dev dependencies)
make api-generate

# 3. Start services (PostgreSQL, Redis, NATS)
make docker-up

# 4. Run database migrations
make migrate

# 5. Seed initial data
make db-seed
```

**Note:** The `make install` command runs `uv sync --all-extras` which installs all dependencies including code generation tools like `datamodel-code-generator`.

### Development

```bash
# Start development server with hot reload
make dev

# Run tests
make test

# Run tests with coverage
make test-cov

# Run linting
make lint

# Format code
make format

# Run type checking
make typecheck

# Run all checks (lint + typecheck + test)
make check
```

### Available Make Commands

Run `make help` to see all available commands.

## API Development (Contract-First)

This project follows **contract-first API development**, where the OpenAPI specification serves as the single source of truth for API models.

### Workflow

```bash
# 1. Design/update API contract
vi openapi.yaml

# 2. Generate Pydantic models from spec
make api-generate

# 3. Models are auto-generated in src/dataminer/api/generated/models.py
# 4. Import and use in your routes
from dataminer.api.generated import DocumentSourceResponse
```

### What's Tracked vs Generated

**✅ Tracked in Git (Source of Truth):**
- `openapi.yaml` - API contract specification
- `src/dataminer/api/generated/__init__.py` - Clean import interface

**❌ Git Ignored (Generated Code):**
- `src/dataminer/api/generated/models.py` - Auto-generated from spec (requires `datamodel-code-generator`, run `make api-generate`)
- `src/dataminer/db/queries/` - Auto-generated from SQLC (run `make sqlc-generate`)
- `sql/schema.sql` - Auto-generated from Alembic (run `make schema-generate`)

### Benefits of Contract-First

- **Single Source of Truth**: OpenAPI spec defines everything
- **No Drift**: Models always match documentation
- **Better Collaboration**: Frontend can work from spec independently
- **Client Generation**: Generate TypeScript/Go/etc clients from same spec
- **API Governance**: Easier contract review and approval

### After Pulling Changes

If someone updated `openapi.yaml`, regenerate the models:

```bash
git pull
make api-generate
```

### Troubleshooting

**Error: "datamodel-code-generator is not installed"**

If you see this error when running `make api-generate`, install development dependencies:

```bash
# Install all dependencies including dev tools
make install

# Or manually sync dependencies
uv sync

# Verify installation
uv run datamodel-codegen --version
```

## Project Structure

```
dataminer/
├── src/
│   └── dataminer/              # Application source code
│       ├── api/                # API endpoints
│       │   ├── generated/      # Generated Pydantic models (run make api-generate)
│       │   ├── v1/             # API version 1 routes
│       │   ├── app.py          # FastAPI application
│       │   └── health.py       # Health check endpoints
│       ├── core/               # Core business logic
│       ├── db/                 # Database models and queries
│       │   ├── models/         # SQLAlchemy ORM models
│       │   ├── repositories/   # Data access layer
│       │   └── queries/        # SQLC generated queries (run make sqlc-generate)
│       ├── services/           # External services integration
│       └── utils/              # Utility functions
├── tests/                      # Test files
├── migrations/                 # Alembic database migrations
│   └── alembic/
│       ├── versions/           # Migration files
│       └── env.py              # Alembic configuration
├── sql/                        # SQL files
│   ├── queries/                # SQLC query definitions
│   └── schema.sql              # Generated schema (run make schema-generate)
├── docs/                       # Documentation
├── PRD/                        # Product requirements
├── openapi.yaml               # API contract specification (source of truth)
├── openapi.json               # API contract (JSON format)
├── Makefile                   # Development commands
├── pyproject.toml             # Project configuration
└── docker-compose.yml         # Local development setup
```

**Note:** Files marked with "run make ..." are auto-generated and git-ignored. Regenerate them locally after pulling changes.

## API Documentation

Once the server is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration

Configuration is managed through environment variables. Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

## Testing

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test file
make test ARGS=tests/test_api.py

# Run specific test
make test ARGS=tests/test_api.py::test_health_check
```

## Database

```bash
# Create new migration
make migration MSG="description of changes"

# Apply migrations
make migrate

# Rollback last migration
make migrate-down

# Reset database (WARNING: destroys all data)
make db-reset

# Seed test data
make db-seed
```

## Code Generation

### API Models (Contract-First)

```bash
# Generate Pydantic models from OpenAPI spec
# Requires: datamodel-code-generator (installed via 'make install')
make api-generate
```

**Important:** After pulling changes to `openapi.yaml`, always run `make api-generate` to regenerate models locally.

### Database Code Generation

```bash
# Generate SQL schema from Alembic models
make schema-generate

# Generate type-safe SQL queries with SQLC
make sqlc-generate
```

## Docker

```bash
# Build Docker image
make docker-build

# Start all services
make docker-up

# Stop all services
make docker-down

# View logs
docker-compose logs -f
```

## Contributing

1. **Setup**: Ensure you have all dev dependencies installed

   ```bash
   make install  # Installs datamodel-code-generator and other dev tools
   ```

2. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - If you modify `openapi.yaml`, run `make api-generate` to regenerate models
   - Follow contract-first principles for API changes

4. **Run all checks** to ensure quality

   ```bash
   make check  # Runs lint + typecheck + tests
   ```

5. **Submit a pull request**

## License

Proprietary - All rights reserved

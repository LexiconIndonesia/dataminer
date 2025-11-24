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
- **Database**: PostgreSQL 16+
- **Migrations**: Alembic
- **SQL**: SQLC for type-safe queries
- **Queue**: NATS JetStream
- **Cache**: Redis 7+
- **Testing**: pytest with async support
- **Containerization**: Docker

## Quick Start

### Prerequisites

- Python 3.14
- UV package manager
- Docker and Docker Compose
- Make

### Installation

```bash
# Install dependencies
make install

# Start services (PostgreSQL, Redis, NATS)
make docker-up

# Run database migrations
make migrate

# Seed initial data
make db-seed
```

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

## Project Structure

```
dataminer/
├── src/
│   └── dataminer/         # Application source code
│       ├── api/           # API endpoints
│       ├── core/          # Core business logic
│       ├── db/            # Database models and queries
│       ├── services/      # External services integration
│       └── utils/         # Utility functions
├── tests/                 # Test files
├── migrations/            # Alembic migrations
├── docs/                  # Documentation
├── PRD/                   # Product requirements
├── Makefile              # Development commands
├── pyproject.toml        # Project configuration
└── docker-compose.yml    # Local development setup
```

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

1. Create a feature branch
2. Make your changes
3. Run `make check` to ensure quality
4. Submit a pull request

## License

Proprietary - All rights reserved

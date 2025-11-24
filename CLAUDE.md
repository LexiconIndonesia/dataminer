# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup
```bash
make install              # Install dependencies with UV
make docker-up            # Start PostgreSQL, Redis, NATS
make api-generate         # Generate Pydantic models from OpenAPI spec
make migrate              # Apply database migrations
```

### Development Workflow
```bash
make dev                  # Start dev server with hot reload
make test                 # Run all tests
make test ARGS=path/to/test.py::test_name  # Run specific test
make test-fast            # Run tests without coverage (faster)
make lint                 # Check code with ruff
make lint-fix             # Auto-fix linting issues
make format               # Format code
make typecheck            # Run mypy type checking
make check                # Run lint + typecheck + test
```

### Database Operations
```bash
make migration MSG="description"  # Create new migration
make migrate              # Apply migrations
make migrate-down         # Rollback one migration
make db-reset             # Reset database (destroys data)
```

### Code Generation
```bash
make api-generate         # Generate Pydantic models from openapi.yaml
make schema-generate      # Generate sql/schema.sql from Alembic models
make sqlc-generate        # Generate type-safe queries (runs schema-generate first)
```

## Architecture Overview

### Contract-First API Development

This project follows **contract-first API development** where `openapi.yaml` is the single source of truth:

1. **Design API contract first**: Edit `openapi.yaml` with endpoint definitions and schemas
2. **Generate code**: Run `make api-generate` to create Pydantic models in `src/dataminer/api/generated/models.py`
3. **Import and use**: Import generated models in route handlers

**Important**: Always run `make api-generate` after pulling changes to `openapi.yaml`. The generated `models.py` is git-ignored and must be regenerated locally.

Example import:
```python
from dataminer.api.generated import DocumentSourceResponse, DocumentSourceCreate
```

### Database Layer Architecture

The project uses multiple database access patterns:

**1. SQLAlchemy ORM Models** (`src/dataminer/db/models/`)
- Define table schemas and relationships
- Used for migrations via Alembic
- Support async operations with `AsyncSession`

**2. Repository Pattern** (`src/dataminer/db/repositories/`)
- Encapsulates database operations
- Takes `AsyncSession` as constructor parameter
- Returns ORM model instances
- Example: `SourceRepository(session).get_source_by_id()`

**3. SQLC Generated Queries** (`src/dataminer/db/queries/`)
- Type-safe SQL queries generated from `sql/queries/*.sql`
- Auto-generated code (git-ignored) - regenerate with `make sqlc-generate`
- Workflow: Define SQL in `sql/queries/` → run `make sqlc-generate` → import from `dataminer.db.queries`

**Database Session Management**:
- Use `Depends(get_db)` in FastAPI endpoints to get `AsyncSession`
- Sessions auto-commit on success, auto-rollback on error
- No need to call `session.commit()` explicitly in endpoints
- See `src/dataminer/db/session.py` for implementation

### Application Structure

**Core Components**:
- `src/dataminer/api/app.py` - FastAPI application factory with lifespan management
- `src/dataminer/core/config.py` - Pydantic settings from environment variables
- `src/dataminer/api/v1/` - API version 1 route handlers
- `src/dataminer/db/models/` - SQLAlchemy ORM models
- `src/dataminer/db/repositories/` - Data access layer
- `src/dataminer/services/` - External service integrations (OCR, LLM, queue)

**Configuration**:
- Settings loaded from `.env` file via `pydantic-settings`
- Access via `get_settings()` singleton
- Copy `.env.example` to `.env` for local development

**Testing**:
- Fixtures in `tests/conftest.py` provide test app, client, and database session
- Use `async_client` fixture for async endpoints
- Use `db_session` fixture for database tests
- Test database is automatically created/dropped per test function

### Generated Code (Git-Ignored)

These files are auto-generated and must be regenerated locally:

1. `src/dataminer/api/generated/models.py` - Run `make api-generate`
2. `src/dataminer/db/queries/*.py` - Run `make sqlc-generate`
3. `sql/schema.sql` - Run `make schema-generate`

After pulling changes, regenerate with:
```bash
make api-generate     # If openapi.yaml changed
make sqlc-generate    # If migrations or sql/queries/*.sql changed
```

### Source of Truth Files (Git-Tracked)

- `openapi.yaml` - API contract specification
- `src/dataminer/db/models/*.py` - Database schema
- `sql/queries/*.sql` - SQL query definitions for SQLC
- `migrations/alembic/versions/*.py` - Database migrations

## Key Development Patterns

### Adding New API Endpoints

1. Update `openapi.yaml` with new endpoint and schemas
2. Run `make api-generate` to regenerate models
3. Import generated models in route handler
4. Add route to appropriate router in `src/dataminer/api/v1/`
5. Use `Depends(get_db)` for database access

### Creating Database Migrations

```bash
# 1. Modify SQLAlchemy models in src/dataminer/db/models/
# 2. Generate migration
make migration MSG="add user table"
# 3. Review migration in migrations/alembic/versions/
# 4. Apply migration
make migrate
# 5. Regenerate schema and SQLC code
make sqlc-generate
```

### Using Repository Pattern

```python
from sqlalchemy.ext.asyncio import AsyncSession
from dataminer.db.repositories import SourceRepository

async def my_endpoint(db: AsyncSession = Depends(get_db)):
    repo = SourceRepository(db)
    source = await repo.get_source_by_id("ID_SC")
    # Changes auto-commit on successful response
    return source
```

### Using SQLC Queries

```python
from dataminer.db.queries import AsyncQuerier

async def my_endpoint(db: AsyncSession = Depends(get_db)):
    querier = AsyncQuerier(db)
    sources = await querier.list_sources()
    return sources
```

## Tech Stack

- **Python**: 3.14
- **Package Manager**: UV (replaces pip/poetry)
- **Web Framework**: FastAPI
- **Database**: PostgreSQL 16+ with asyncpg driver
- **ORM**: SQLAlchemy 2.0 async
- **Migrations**: Alembic
- **Query Builder**: SQLC for type-safe SQL
- **Queue**: NATS JetStream
- **Cache**: Redis 7+
- **Testing**: pytest with pytest-asyncio
- **Code Quality**: ruff (linter + formatter), mypy (type checker)

## Dependencies

Run all commands with `uv run` prefix (e.g., `uv run pytest`). The `Makefile` handles this automatically.

When adding dependencies:
```bash
uv add package-name              # Production dependency
uv add --dev package-name        # Dev dependency
```

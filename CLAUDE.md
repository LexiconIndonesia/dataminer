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
make sqlc-generate        # Generate type-safe queries (uses committed schema)
make schema-generate      # Regenerate schema from database (after migrations)
make regenerate-all       # Regenerate schema + SQLC code (after migrations)
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

### Database Layer Architecture (ORM-Free)

This project **does not use SQLAlchemy ORM**. Database access uses:

**1. Alembic for Migrations** (`migrations/alembic/versions/`)
- Manual SQL migrations (no autogenerate)
- Write raw SQL DDL in migration files
- Run `make migration MSG="description"` to create new migration file
- Run `make migrate` to apply migrations

**2. SQLC for Type-Safe Queries** (`src/dataminer/db/queries/`)
- Define queries in `sql/queries/*.sql`
- SQLC generates Python dataclasses and async query methods
- Auto-generated code (git-ignored) - regenerate with `make sqlc-generate`
- Returns dataclass instances (not ORM models)

**3. Repository Pattern** (`src/dataminer/db/repositories/`)
- Thin wrappers around SQLC queries
- Takes `AsyncSession` as constructor parameter
- Handles business logic, not ORM relationships
- Returns SQLC dataclass instances
- Example: `SourceRepository(session).get_source_by_id()`

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
- `src/dataminer/db/queries/` - SQLC generated dataclasses and query methods
- `src/dataminer/db/repositories/` - Data access layer using SQLC
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

After pulling changes, regenerate with:
```bash
make api-generate     # If openapi.yaml changed
make sqlc-generate    # If sql/queries/*.sql changed
```

### Schema Files (Git-Tracked)

The `sql/schema/current_schema.sql` file is **committed to git**. This allows CI to generate SQLC code without a running database.

After creating new migrations, regenerate and commit the schema:
```bash
make migrate           # Apply migrations
make regenerate-all    # Regenerate schema + SQLC code
git add sql/schema/    # Commit the updated schema
```

### Source of Truth Files (Git-Tracked)

- `openapi.yaml` - API contract specification
- `sql/queries/*.sql` - SQL query definitions for SQLC
- `sql/schema/current_schema.sql` - Database schema snapshot for SQLC
- `migrations/alembic/versions/*.py` - Database migrations (source of truth for schema evolution)

## Key Development Patterns

### Adding New API Endpoints

1. Update `openapi.yaml` with new endpoint and schemas
2. Run `make api-generate` to regenerate models
3. Import generated models in route handler
4. Add route to appropriate router in `src/dataminer/api/v1/`
5. Use `Depends(get_db)` for database access

### Creating Database Migrations

This project uses **manual SQL migrations** (not autogenerate):

```bash
# 1. Create new migration file
make migration MSG="add user table"

# 2. Edit the migration file in migrations/alembic/versions/
# Write raw SQL in the upgrade() and downgrade() functions:
#   op.execute("CREATE TABLE users (...)")
#   op.execute("DROP TABLE users")

# 3. Apply migration
make migrate

# 4. Regenerate schema and SQLC code
make regenerate-all

# 5. Commit both migration and updated schema
git add migrations/ sql/schema/
git commit -m "Add user table migration"
```

**Important**: Always write both `upgrade()` and `downgrade()` SQL for reversibility.
**Important**: Always commit the updated `sql/schema/current_schema.sql` along with migrations.

### Using Repository Pattern

Repositories return SQLC dataclasses, which FastAPI automatically serializes:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dataminer.db.repositories.source import SourceRepository
from dataminer.db.session import get_db

async def my_endpoint(db: AsyncSession = Depends(get_db)):
    repo = SourceRepository(db)
    source = await repo.get_source_by_id("ID_SC")
    # Returns SQLC dataclass
    # Changes auto-commit on successful response
    return source  # FastAPI serializes dataclass to JSON
```

### Using SQLC Queries Directly

For simpler queries, you can bypass repositories and use SQLC directly:

```python
from dataminer.db.queries import sources

async def my_endpoint(db: AsyncSession = Depends(get_db)):
    conn = await db.connection()
    querier = sources.AsyncQuerier(conn)
    sources_list = await querier.list_sources()
    return sources_list  # Returns list of dataclasses
```

### Type Separation: SQLC vs OpenAPI

- **SQLC types** (`dataminer.db.queries.models`): Database layer dataclasses
- **OpenAPI types** (`dataminer.api.generated`): API request/response Pydantic models
- FastAPI automatically converts SQLC dataclasses to OpenAPI response models via `response_model`
- For requests, manually map OpenAPI models to repository method parameters

## Tech Stack

- **Python**: 3.14
- **Package Manager**: UV (replaces pip/poetry)
- **Web Framework**: FastAPI
- **Database**: PostgreSQL 16+ with asyncpg driver
- **Migrations**: Alembic (manual SQL migrations)
- **Query Builder**: SQLC for type-safe SQL queries
- **Queue**: NATS JetStream
- **Cache**: Redis 7+
- **Testing**: pytest with pytest-asyncio
- **Code Quality**: ruff (linter + formatter), mypy (type checker)

**Note**: This project does not use SQLAlchemy ORM. Database access is through SQLC-generated type-safe queries.

## Dependencies

Run all commands with `uv run` prefix (e.g., `uv run pytest`). The `Makefile` handles this automatically.

When adding dependencies:
```bash
uv add package-name              # Production dependency
uv add --dev package-name        # Dev dependency
```
- Always run pre-commit after doing a task
- Always run the tests after making changes, make sure all the tests pass

# General Project Tasks - Dataminer Service

**Status:** Phase 1 - Implementation
**Last Updated:** 2024-11-24

---

## Developer Interface Note

**Primary Interface:** All development tasks use **Make commands** as the standard interface.

**Example:**
- ✅ Use: `make test`, `make lint`, `make migrate`
- ❌ Avoid: `uv run pytest`, `uv run ruff check`, `uv run alembic upgrade head`

Make provides a consistent, documented interface that wraps UV commands. This ensures:
- Consistent commands across all developers
- Easy discoverability via `make help`
- Cross-platform compatibility
- Simplified onboarding for new developers

See the Summary section at the end for a complete reference of all Make commands.

---

## 0. Project Setup and Infrastructure

### Task 0.1: Initial Project Structure

**Actionable Items:**
- [ ] Initialize Python project with UV for dependency management
- [ ] Set up project directory structure (src, tests, migrations, docs)
- [ ] Create .gitignore for Python projects
- [ ] Initialize git repository
- [ ] Create README.md with project overview
- [ ] Configure UV to use Python 3.14
- [ ] Set up pyproject.toml with project metadata

**Positive Cases:**
- UV successfully initializes project
- Directory structure follows best practices
- All necessary config files present
- Python 3.14 correctly configured

**Negative Cases:**
- Handle existing directory (don't overwrite)
- Missing Python 3.14 installation
- UV not installed

**Edge Cases:**
- Pre-existing .git directory
- Custom UV configuration
- Multiple Python versions installed

**Test Scenarios:**
```
Test: Verify project structure is created correctly
- Assert all required directories exist (src, tests, migrations, docs, PRD)
- Assert pyproject.toml exists with correct dependencies
- Assert .gitignore includes Python-specific patterns

Test: Verify UV environment setup
- Assert Python version is 3.14
- Assert UV virtual environment is created
- Assert dev dependencies are installed
- Assert UV lock file generated

Test: Make commands work correctly
- Run make install to sync dependencies via UV
- Run make test to execute tests via UV
- Run make help to show available targets
- Assert all commands execute successfully
```

---

### Task 0.2: FastAPI Application Setup

**Actionable Items:**
- [ ] Set up FastAPI application with proper structure
- [ ] Implement application factory pattern
- [ ] Add CORS middleware configuration
- [ ] Add request/response logging middleware
- [ ] Add error handling middleware
- [ ] Configure application settings with Pydantic BaseSettings
- [ ] Add health check endpoint
- [ ] Set up API versioning (v1)
- [ ] Configure OpenAPI documentation
- [ ] Add request ID tracking

**Positive Cases:**
- FastAPI app starts successfully
- Health check endpoint returns 200
- OpenAPI docs accessible at /docs
- API versioning working (/api/v1/...)
- CORS headers properly configured

**Negative Cases:**
- Handle startup failures gracefully
- Invalid configuration raises clear errors
- Missing environment variables use defaults

**Edge Cases:**
- Multiple instances running (port conflicts)
- Very large request payloads
- Malformed JSON in requests

**Test Scenarios:**
```
Test: Health check endpoint
- GET /health returns 200
- Response includes app version and status

Test: API versioning
- Routes prefixed with /api/v1
- Invalid version prefix returns 404

Test: CORS configuration
- OPTIONS request includes proper CORS headers
- Allowed origins respected

Test: Error handling
- 404 returns proper JSON error response
- 422 validation error includes field details
- 500 internal error doesn't leak stack trace in production
```

---

### Task 0.3: Database Setup with Alembic

**Actionable Items:**
- [ ] Install and initialize Alembic
- [ ] Configure Alembic for PostgreSQL
- [ ] Set up environment-based database URLs
- [ ] Create initial migration for schema creation
- [ ] Add migration for public schema tables
- [ ] Add migration for id_sc schema tables
- [ ] Create migration helpers for data seeding
- [ ] Add downgrade migrations for all changes
- [ ] Set up migration testing

**Positive Cases:**
- Alembic initializes successfully
- Migrations run without errors
- Schema created correctly
- Downgrade works without data loss
- Seed data inserted correctly

**Negative Cases:**
- Handle existing database (don't re-create)
- Handle failed migration (rollback)
- Handle conflicts in schema

**Edge Cases:**
- Running same migration twice (idempotency)
- Downgrading multiple versions
- Partial migration failure

**Test Scenarios:**
```
Test: Initial migration creates schemas
- Run migration: creates public and id_sc schemas
- Verify all tables exist in correct schemas
- Verify all indexes created

Test: Migration idempotency
- Run same migration twice
- Assert no errors, no duplicate tables

Test: Downgrade migration
- Apply migration, then downgrade
- Assert schemas and tables removed
- Assert no orphaned data

Test: Seed data migration
- Run seed migration
- Verify ID_SC source exists in document_sources
- Verify default profile exists
```

---

### Task 0.4: SQLC Setup for Type-Safe SQL

**Actionable Items:**
- [x] Install and configure sqlc
- [x] Create sqlc.yaml configuration
- [x] Define SQL queries in sql/ directory
- [x] Configure sqlc for Python/PostgreSQL
- [x] Generate type-safe query functions
- [x] Integrate generated code with FastAPI
- [x] Add sqlc generation to CI/CD (via Makefile)
- [x] Create queries for all configuration tables
- [x] Create queries for extraction operations
- [x] Create schema generator from Alembic models

**Positive Cases:**
- sqlc generates valid Python code
- Generated functions have proper type hints
- Queries execute without errors
- Complex joins work correctly

**Negative Cases:**
- Handle invalid SQL syntax
- Handle missing query parameters
- Handle database connection errors

**Edge Cases:**
- Queries with optional parameters
- Queries returning large result sets
- Complex aggregation queries

**Test Scenarios:**
```
Test: Generate code from SQL
- Write SQL query in sql/ directory
- Run sqlc generate
- Assert Python code generated in correct location
- Assert type hints present

Test: Query execution
- Use generated function to insert record
- Use generated function to query record
- Assert results match expected type

Test: Parameterized queries
- Execute query with parameters
- Assert SQL injection prevented
- Assert parameters properly escaped
```

---

### Task 0.5: Docker and Docker Compose Setup

**Actionable Items:**
- [ ] Create Dockerfile for application with Python 3.14
- [ ] Use multi-stage build for optimization
- [ ] Use UV for dependency installation in Docker
- [ ] Create docker-compose.yml for local development
- [ ] Add PostgreSQL service (version 16+)
- [ ] Add Redis service (version 7+)
- [ ] Add NATS service (optional for local dev)
- [ ] Add development vs production compose files
- [ ] Configure volume mounts for development
- [ ] Add healthchecks for all services
- [ ] Create .env.example file

**Positive Cases:**
- Docker image builds successfully with Python 3.14
- UV installs dependencies correctly in container
- All services start with docker-compose up
- Application connects to all services
- Hot reload works in development mode
- Database persists data across restarts

**Negative Cases:**
- Handle missing environment variables
- Handle port conflicts
- Handle service startup failures
- Handle UV cache issues in Docker

**Edge Cases:**
- Services starting out of order
- Database not ready when app starts
- Volume permission issues
- UV lock file changes during build

**Test Scenarios:**
```
Test: Docker build with Python 3.14
- Build Docker image
- Assert build succeeds
- Assert Python version is 3.14
- Assert UV is installed
- Assert image size reasonable (<500MB)

Test: Docker Compose services
- Start all services with docker-compose up
- Assert PostgreSQL accessible on port 5432
- Assert Redis accessible on port 6379
- Assert FastAPI app responds to health check

Test: Service dependencies
- Stop PostgreSQL
- Assert app handles connection loss gracefully
- Restart PostgreSQL
- Assert app reconnects automatically

Test: Data persistence
- Create data in PostgreSQL
- Restart containers
- Assert data still exists

Test: Development hot reload
- Change Python file
- Assert app reloads automatically
- Assert changes reflected
```

---

### Task 0.6: OpenAPI Contract and Code Generation

**Actionable Items:**
- [ ] Configure FastAPI OpenAPI generation
- [ ] Customize OpenAPI schema with descriptions
- [ ] Add example values to all models
- [ ] Generate OpenAPI spec JSON/YAML
- [ ] Set up openapi-generator for client SDK
- [ ] Generate Pydantic models from OpenAPI
- [ ] Generate API client code
- [ ] Version OpenAPI specs
- [ ] Add OpenAPI validation to CI
- [ ] Generate TypeScript types for frontend (optional)

**Positive Cases:**
- OpenAPI spec generates correctly
- Spec includes all endpoints
- Models include validation rules
- Generated client works correctly
- Examples in docs are accurate

**Negative Cases:**
- Handle invalid model definitions
- Handle missing response models
- Validate spec against OpenAPI 3.0 standard

**Edge Cases:**
- Deeply nested models
- Circular model references
- Union types and polymorphism

**Test Scenarios:**
```
Test: OpenAPI spec generation
- Generate OpenAPI spec
- Assert all endpoints included
- Assert all models included
- Validate spec against OpenAPI 3.0 schema

Test: Generated Pydantic models
- Generate models from spec
- Assert all fields have correct types
- Assert validation rules present
- Test model instantiation

Test: Request/Response models
- Assert all endpoints have response models
- Assert 422 responses documented
- Assert examples provided

Test: OpenAPI spec versioning
- Update API, bump version
- Assert old version spec still accessible
- Assert breaking changes flagged
```

---

### Task 0.7: Test Suite Setup

**Actionable Items:**
- [ ] Set up pytest with async support
- [ ] Configure pytest-cov for coverage reporting
- [ ] Set up pytest-asyncio for async tests
- [ ] Create test fixtures for database
- [ ] Create test fixtures for API client
- [ ] Set up test database (separate from dev)
- [ ] Configure test data factories
- [ ] Add pytest-mock for mocking
- [ ] Set up integration test markers
- [ ] Configure coverage thresholds (>80%)
- [ ] Add test report generation

**Positive Cases:**
- All tests run successfully
- Coverage report generated
- Fixtures work correctly
- Test database isolated from dev
- Integration tests marked correctly

**Negative Cases:**
- Handle test database creation failures
- Handle missing test data
- Clean up test data after failures

**Edge Cases:**
- Parallel test execution
- Tests with external dependencies
- Flaky tests (retry logic)

**Test Scenarios:**
```
Test: Pytest configuration
- Run pytest
- Assert configuration loaded from pyproject.toml
- Assert test discovery works
- Assert markers registered

Test: Database fixtures
- Use db fixture in test
- Assert test database used (not dev database)
- Assert transactions rolled back after test
- Assert fixtures can be nested

Test: API client fixtures
- Use client fixture
- Assert test client doesn't require server running
- Assert database changes visible to client

Test: Coverage reporting
- Run pytest with coverage
- Assert coverage report generated
- Assert coverage threshold enforced
- Assert uncovered lines reported
```

---

### Task 0.8: GitHub Actions CI/CD

**Actionable Items:**
- [ ] Create .github/workflows/pr-checks.yml
- [ ] Use Make commands in CI for consistency
- [ ] Add `make lint` for linting checks (ruff, mypy)
- [ ] Add `make format` check for code formatting
- [ ] Add `make test-cov` for test execution with coverage
- [ ] Add coverage reporting to PR comments
- [ ] Add security scanning (bandit via Make target)
- [ ] Add dependency vulnerability scanning
- [ ] Create .github/workflows/build.yml for Docker builds
- [ ] Add `make migrate` check for migration validation
- [ ] Add `make openapi` for OpenAPI spec validation
- [ ] Configure branch protection rules
- [ ] Add status badges to README
- [ ] Cache UV dependencies for faster CI
- [ ] Use matrix strategy for Python 3.14

**Positive Cases:**
- PR checks run on every pull request using Make commands
- All Make targets work in CI environment
- Linting passes (make lint)
- Tests pass with coverage (make test-cov)
- Docker image builds (make docker-build)
- No security issues found
- UV cache speeds up subsequent runs

**Negative Cases:**
- PR checks fail on linting errors
- PR checks fail on test failures
- PR checks fail on low coverage
- PR checks fail on security issues
- Make command not found (should install Make)

**Edge Cases:**
- Very large PRs (timeout handling)
- Flaky tests (retry logic with make test)
- External service dependencies
- UV cache corruption
- Parallel job execution

**Test Scenarios:**
```
Test: CI uses Make commands consistently
- Inspect workflow YAML
- Assert all steps use make commands
- Assert no direct uv run commands in CI
- Assert make install runs first

Test: PR lint checks with Make
- Create PR with linting errors
- Assert workflow runs make lint
- Assert workflow fails
- Fix errors
- Assert make lint passes in CI

Test: PR test checks with Make
- Create PR with failing tests
- Assert workflow runs make test-cov
- Assert workflow fails
- Fix tests
- Assert make test-cov passes in CI

Test: PR formatting checks with Make
- Create PR with unformatted code
- Assert workflow runs make format check
- Assert workflow fails
- Format code with make format
- Assert workflow passes

Test: PR coverage checks with Make
- Create PR that reduces coverage
- Assert make test-cov reports coverage
- Assert workflow fails if below threshold
- Add tests to increase coverage
- Assert workflow passes

Test: Docker build workflow with Make
- Push to main branch
- Assert workflow runs make docker-build
- Assert Docker image built
- Assert image tagged with commit SHA
- Assert image pushed to registry

Test: Migration validation with Make
- Create PR with migration
- Assert workflow runs make migrate
- Assert migration applies successfully
- Assert make migrate-down rolls back
- Assert make db-seed loads data

Test: UV cache in CI
- First CI run caches UV dependencies
- Second CI run uses cache
- Assert second run faster than first
- Assert cache key based on uv.lock

Test: Make help in CI
- Run make help in CI
- Assert all targets documented
- Assert no errors in help output
```

---

### Task 0.9: Development Tools and Scripts

**Actionable Items:**
- [ ] Create comprehensive Makefile as primary developer interface
- [ ] Add `make install` target (wraps uv sync)
- [ ] Add `make dev` target to run development server
- [ ] Add `make test` target (wraps uv run pytest)
- [ ] Add `make test-cov` target for coverage reports
- [ ] Add `make lint` target (wraps uv run ruff check)
- [ ] Add `make format` target (wraps uv run ruff format)
- [ ] Add `make typecheck` target (wraps uv run mypy)
- [ ] Add `make migrate` target (wraps uv run alembic upgrade head)
- [ ] Add `make migrate-down` target (wraps uv run alembic downgrade -1)
- [ ] Add `make migration` target to create new migration
- [ ] Add `make db-reset` target for database reset
- [ ] Add `make db-seed` target for test data generation
- [ ] Add `make docker-build` target
- [ ] Add `make docker-up` and `make docker-down` targets
- [ ] Add `make openapi` target for spec generation
- [ ] Add `make sqlc-generate` target
- [ ] Add `make clean` target to clean artifacts
- [ ] Add `make check` target to run all checks (lint, typecheck, test)
- [ ] Add pre-commit hooks that use Make targets
- [ ] Create development documentation emphasizing Make commands
- [ ] Add help text to Makefile (make help)

**Positive Cases:**
- All Make commands work correctly
- Make provides consistent interface across environments
- UV commands properly wrapped by Make
- Dependencies installed via make install
- Pre-commit hooks use Make targets
- Help text displays all available targets

**Negative Cases:**
- Handle missing Make installation
- Handle missing UV installation
- Handle missing dependencies
- Handle script failures gracefully
- Prevent destructive operations in production

**Edge Cases:**
- Make running on different OS (Linux/macOS/Windows with WSL)
- Missing environment variables
- Database not running (docker-compose not started)
- UV cache issues
- Parallel make execution

**Test Scenarios:**
```
Test: Makefile help and structure
- Run make help
- Assert all targets documented
- Assert targets grouped by category (setup, dev, test, db, docker)

Test: Installation and setup
- Run make install
- Assert UV syncs dependencies
- Assert virtual environment created
- Assert all dependencies available

Test: Development workflow
- Run make dev
- Assert FastAPI server starts
- Assert hot reload enabled
- Assert server accessible on correct port

Test: Testing targets
- Run make test
- Assert all tests execute with UV
- Run make test-cov
- Assert coverage report generated
- Assert coverage threshold checked

Test: Code quality targets
- Run make lint
- Assert ruff check executes via UV
- Run make format
- Assert ruff format executes via UV
- Run make typecheck
- Assert mypy executes via UV
- Run make check
- Assert all checks run in sequence

Test: Database targets
- Run make migrate
- Assert Alembic migrations applied via UV
- Run make migrate-down
- Assert migration rolled back
- Run make db-reset
- Assert database dropped and recreated
- Run make db-seed
- Assert test data loaded

Test: Docker targets
- Run make docker-build
- Assert Docker image builds
- Run make docker-up
- Assert all services start
- Run make docker-down
- Assert all services stop

Test: Code generation targets
- Run make openapi
- Assert OpenAPI spec generated
- Run make sqlc-generate
- Assert SQLC code generated

Test: Pre-commit integration
- Attempt commit with unformatted code
- Assert pre-commit runs make format
- Assert commit blocked if check fails
- Format code manually with make format
- Assert commit succeeds

Test: Cross-platform compatibility
- Run make commands on Linux
- Run make commands on macOS
- Run make commands on Windows WSL
- Assert all commands work consistently
```

---

## 1. Database Schema Setup - Public Schema

### Task 1.1: Create Public Schema Configuration Tables

**Actionable Items:**
- [x] Create migration script for `public.document_sources` table
- [x] Create migration script for `public.source_extraction_profiles` table
- [x] Create migration script for `public.source_field_definitions` table
- [x] Create migration script for `public.source_normalization_rules` table
- [x] Create migration script for `public.source_prompt_templates` table
- [x] Create all necessary indexes for performance
- [x] Add foreign key constraints with proper cascade behavior
- [x] Seed initial data for ID_SC source

**Positive Cases:**
- Successfully create all tables without errors
- Insert ID_SC source configuration
- Create default extraction profile for ID_SC
- Add field definitions for all 77 ID_SC fields
- Create normalization rules for Indonesian legal terms
- Add prompt templates for ID_SC sections

**Negative Cases:**
- Handle duplicate source_id insertion (ON CONFLICT)
- Reject invalid foreign key references
- Prevent deletion of source with active profiles
- Handle constraint violations gracefully
- Validate JSONB fields for validation_rules and normalization_rules

**Edge Cases:**
- Source with multiple active profiles (ensure is_default flag works)
- Field definition with no validation rules (null JSONB)
- Normalization rule with regex special characters
- Prompt template with large text (>10KB)
- Multiple templates with same name but different versions

**Unit Tests:**
```python
def test_create_document_source():
    """Test creating a new document source"""
    source = create_source(
        source_id="ID_SC",
        source_name="Indonesian Supreme Court",
        country_code="IDN",
        primary_language="id"
    )
    assert source.source_id == "ID_SC"
    assert source.is_active is True

def test_duplicate_source_id():
    """Test handling duplicate source_id"""
    create_source(source_id="ID_SC", ...)
    with pytest.raises(IntegrityError):
        create_source(source_id="ID_SC", ...)

def test_create_extraction_profile():
    """Test creating extraction profile with valid config"""
    profile = create_profile(
        source_id="ID_SC",
        profile_name="Default Profile",
        llm_model_detailed="gemini-1.5-pro"
    )
    assert profile.is_active is True
    assert profile.version == 1

def test_field_definition_with_validation_rules():
    """Test field definition with JSONB validation rules"""
    field = create_field_definition(
        source_id="ID_SC",
        field_name="defendant_name",
        validation_rules={"max_length": 200, "required": True}
    )
    assert field.validation_rules["max_length"] == 200

def test_invalid_foreign_key():
    """Test profile creation with non-existent source_id"""
    with pytest.raises(ForeignKeyViolation):
        create_profile(source_id="INVALID", ...)
```

**Integration Tests:**
```python
def test_full_configuration_flow():
    """Test complete configuration setup for new source"""
    # Create source
    source = create_source(source_id="ID_SC", ...)

    # Create profile
    profile = create_profile(source_id="ID_SC", ...)

    # Add field definitions
    fields = []
    for field_name in ["case_number", "defendant_name", ...]:
        field = create_field_definition(
            source_id="ID_SC",
            field_name=field_name,
            ...
        )
        fields.append(field)

    # Add normalization rules
    rules = create_normalization_rules(source_id="ID_SC", ...)

    # Add prompt templates
    templates = create_prompt_templates(source_id="ID_SC", ...)

    # Verify all created
    assert len(fields) == 77
    assert profile.is_default is True
    assert len(rules) > 0
    assert len(templates) > 0
```

---

## 2. Configuration Management API

### Task 2.1: Source Management Endpoints

**Actionable Items:**
- [x] Implement `GET /v1/dataminer/sources` - List all sources
- [x] Implement `GET /v1/dataminer/sources/{source_id}` - Get source details
- [x] Implement `PUT /v1/dataminer/sources/{source_id}/config` - Update source config
- [x] Implement `POST /v1/dataminer/sources/{source_id}/profiles` - Create profile
- [x] Add request validation with Pydantic models
- [x] Add response serialization
- [x] Add error handling and appropriate HTTP status codes
- [x] Add API documentation with OpenAPI/Swagger

**Positive Cases:**
- List all sources returns array of source objects
- Get specific source returns full configuration
- Update source configuration succeeds
- Create new profile succeeds with valid data
- Filter sources by country_code
- Filter sources by language
- Include statistics in source details

**Negative Cases:**
- GET non-existent source returns 404
- PUT with invalid source_id returns 404
- POST profile with duplicate name returns 409
- Request with invalid JSON returns 422
- Missing required fields returns 400
- Unauthorized access returns 401

**Edge Cases:**
- List sources with no results returns empty array
- Get source with 0 profiles
- Update source while jobs are running
- Create profile with all optional fields omitted (use defaults)
- Very long profile_name (boundary testing)

**Unit Tests:**
```python
def test_list_sources_empty():
    """Test listing sources when none exist"""
    response = client.get("/v1/dataminer/sources")
    assert response.status_code == 200
    assert response.json() == []

def test_list_sources_with_data():
    """Test listing sources with existing data"""
    create_source(source_id="ID_SC", ...)
    create_source(source_id="SG_SC", ...)

    response = client.get("/v1/dataminer/sources")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_source_by_id():
    """Test retrieving specific source"""
    create_source(source_id="ID_SC", ...)

    response = client.get("/v1/dataminer/sources/ID_SC")
    assert response.status_code == 200
    assert response.json()["source_id"] == "ID_SC"

def test_get_nonexistent_source():
    """Test retrieving non-existent source"""
    response = client.get("/v1/dataminer/sources/INVALID")
    assert response.status_code == 404

def test_update_source_config():
    """Test updating source configuration"""
    create_source(source_id="ID_SC", ...)

    response = client.put(
        "/v1/dataminer/sources/ID_SC/config",
        json={"avg_cost_per_document": 1.75}
    )
    assert response.status_code == 200
    assert response.json()["avg_cost_per_document"] == 1.75

def test_create_profile():
    """Test creating new extraction profile"""
    create_source(source_id="ID_SC", ...)

    response = client.post(
        "/v1/dataminer/sources/ID_SC/profiles",
        json={
            "profile_name": "High Accuracy Profile",
            "llm_model_detailed": "gemini-1.5-pro",
            "max_cost_per_document": 3.00
        }
    )
    assert response.status_code == 201
    assert response.json()["profile_name"] == "High Accuracy Profile"

def test_create_duplicate_profile():
    """Test creating profile with duplicate name"""
    create_source(source_id="ID_SC", ...)
    create_profile(source_id="ID_SC", profile_name="Default", ...)

    response = client.post(
        "/v1/dataminer/sources/ID_SC/profiles",
        json={"profile_name": "Default", ...}
    )
    assert response.status_code == 409
```

**Integration Tests:**
```python
@pytest.mark.integration
def test_source_lifecycle():
    """Test complete source lifecycle"""
    # Create source
    response = client.post("/v1/dataminer/sources", json={
        "source_id": "TEST_SC",
        "source_name": "Test Court",
        ...
    })
    assert response.status_code == 201

    # List sources
    response = client.get("/v1/dataminer/sources")
    assert any(s["source_id"] == "TEST_SC" for s in response.json())

    # Get source details
    response = client.get("/v1/dataminer/sources/TEST_SC")
    assert response.status_code == 200

    # Update source
    response = client.put(
        "/v1/dataminer/sources/TEST_SC/config",
        json={"is_active": False}
    )
    assert response.status_code == 200

    # Verify update
    response = client.get("/v1/dataminer/sources/TEST_SC")
    assert response.json()["is_active"] is False
```

---

## 3. Field Management API

### Task 3.1: Field Definition Endpoints

**Actionable Items:**
- [x] Implement `GET /v1/dataminer/sources/{source_id}/fields` - List fields
- [x] Implement `POST /v1/dataminer/sources/{source_id}/fields` - Create field
- [x] Implement `GET /v1/dataminer/fields/{field_id}` - Get field details
- [x] Implement `PUT /v1/dataminer/fields/{field_id}` - Update field
- [x] Implement `DELETE /v1/dataminer/fields/{field_id}` - Delete field
- [x] Add filtering by category, field_type, is_required
- [x] Add pagination for large field lists
- [ ] Add field extraction statistics

**Positive Cases:**
- List all fields for a source
- Filter fields by category (critical, important, standard)
- Create new field with full configuration
- Update field extraction method
- Delete unused field
- Get field with extraction statistics

**Negative Cases:**
- List fields for non-existent source returns 404
- Create field with duplicate field_name returns 409
- Update non-existent field returns 404
- Delete field in use by active jobs returns 409
- Invalid field_type returns 400

**Edge Cases:**
- Source with 100+ fields (pagination)
- Field with very long llm_prompt_template (>5KB)
- Field with null validation_rules
- Field with complex nested JSONB validation_rules
- Update field while jobs are using it

**Unit Tests:**
```python
def test_list_fields_for_source():
    """Test listing fields for a specific source"""
    create_source(source_id="ID_SC", ...)
    create_field(source_id="ID_SC", field_name="case_number", ...)
    create_field(source_id="ID_SC", field_name="defendant_name", ...)

    response = client.get("/v1/dataminer/sources/ID_SC/fields")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_filter_fields_by_category():
    """Test filtering fields by category"""
    create_source(source_id="ID_SC", ...)
    create_field(source_id="ID_SC", field_category="critical", ...)
    create_field(source_id="ID_SC", field_category="standard", ...)

    response = client.get(
        "/v1/dataminer/sources/ID_SC/fields?category=critical"
    )
    assert response.status_code == 200
    assert all(f["field_category"] == "critical" for f in response.json())

def test_create_field():
    """Test creating new field definition"""
    create_source(source_id="ID_SC", ...)

    response = client.post(
        "/v1/dataminer/sources/ID_SC/fields",
        json={
            "field_name": "verdict_date",
            "field_type": "date",
            "field_category": "critical",
            "extraction_method": "llm",
            "confidence_threshold": 0.90
        }
    )
    assert response.status_code == 201
    assert response.json()["field_name"] == "verdict_date"

def test_update_field():
    """Test updating field configuration"""
    create_source(source_id="ID_SC", ...)
    field = create_field(source_id="ID_SC", field_name="test_field", ...)

    response = client.put(
        f"/v1/dataminer/fields/{field.field_id}",
        json={"confidence_threshold": 0.85}
    )
    assert response.status_code == 200
    assert response.json()["confidence_threshold"] == 0.85

def test_delete_field():
    """Test deleting field"""
    create_source(source_id="ID_SC", ...)
    field = create_field(source_id="ID_SC", field_name="temp_field", ...)

    response = client.delete(f"/v1/dataminer/fields/{field.field_id}")
    assert response.status_code == 204

    # Verify deletion
    response = client.get(f"/v1/dataminer/fields/{field.field_id}")
    assert response.status_code == 404
```

---

## 4. Job Processing Infrastructure

### Task 4.1: Job Queue Management

**Actionable Items:**
- [ ] Set up NATS JetStream connection
- [ ] Create job queue with priority support
- [ ] Implement job consumer/worker
- [ ] Add job status tracking in Redis
- [ ] Implement job retry mechanism with exponential backoff
- [ ] Add job timeout handling
- [ ] Add dead letter queue for failed jobs
- [ ] Implement graceful shutdown for workers

**Positive Cases:**
- Submit job successfully
- Job moves through states: queued � processing � completed
- Worker picks up job from queue
- Job completes successfully
- Job status updates reflected in Redis
- Multiple workers process jobs concurrently

**Negative Cases:**
- Job fails and moves to retry queue
- Job exceeds max retries and moves to dead letter queue
- Worker crashes during processing (job requeued)
- Queue connection lost (reconnection)
- Invalid job payload rejected

**Edge Cases:**
- High priority job bypasses queue
- Worker shutdown during job processing
- Redis connection lost (fallback to DB)
- Queue full (backpressure)
- Job with 0 retries configured

**Unit Tests:**
```python
def test_submit_job_to_queue():
    """Test submitting job to NATS queue"""
    job = submit_job(
        source_id="ID_SC",
        document_url="https://example.com/doc.pdf",
        priority=5
    )
    assert job.status == "queued"
    assert job.priority == 5

def test_job_status_tracking():
    """Test job status updates in Redis"""
    job = submit_job(...)

    # Check initial status
    status = get_job_status(job.job_id)
    assert status == "queued"

    # Update status
    update_job_status(job.job_id, "processing")
    status = get_job_status(job.job_id)
    assert status == "processing"

def test_job_retry_on_failure():
    """Test job retry mechanism"""
    job = submit_job(..., max_retries=3)

    # Simulate failure
    fail_job(job.job_id, error="Temporary error")

    # Should be requeued
    job = get_job(job.job_id)
    assert job.retry_count == 1
    assert job.status == "queued"

def test_job_dead_letter_after_max_retries():
    """Test job moves to DLQ after max retries"""
    job = submit_job(..., max_retries=2)

    # Fail 3 times
    for _ in range(3):
        fail_job(job.job_id, error="Persistent error")

    job = get_job(job.job_id)
    assert job.status == "failed"
    assert job.retry_count == 2
```

**Integration Tests:**
```python
@pytest.mark.integration
def test_end_to_end_job_processing():
    """Test complete job processing flow"""
    # Submit job
    job = submit_job(
        source_id="ID_SC",
        document_url="https://example.com/test.pdf"
    )

    # Worker picks up job
    worker = JobWorker()
    worker.start()

    # Wait for processing
    wait_for_job_completion(job.job_id, timeout=60)

    # Verify completion
    job = get_job(job.job_id)
    assert job.status == "completed"
    assert job.cost_total > 0

    worker.stop()
```

---

## 5. PDF Processing Pipeline

### Task 5.1: PDF Extraction and OCR

**Actionable Items:**
- [ ] Implement PDF text extraction with pdfplumber
- [ ] Add fallback to PyMuPDF
- [ ] Implement OCR quality detection
- [ ] Integrate Tesseract OCR for Indonesian language
- [ ] Add Google Document AI as fallback for low-quality scans
- [ ] Implement page-level extraction
- [ ] Add text quality metrics
- [ ] Cache extracted text in GCS

**Positive Cases:**
- Extract text from searchable PDF
- Detect high-quality text (no OCR needed)
- Extract text from mixed text/image PDF
- OCR scanned document successfully
- Handle multi-page documents (100+ pages)
- Extract document metadata

**Negative Cases:**
- Handle corrupted PDF file
- Handle password-protected PDF
- Handle PDF with no extractable text
- OCR fails (use Document AI fallback)
- File too large (>100MB)

**Edge Cases:**
- PDF with 1 page
- PDF with 1000+ pages
- PDF with mixed languages
- PDF with tables and images
- Rotated pages in PDF
- PDF with unusual page sizes

**Unit Tests:**
```python
def test_extract_text_from_searchable_pdf():
    """Test extracting text from searchable PDF"""
    text = extract_pdf_text("tests/fixtures/searchable.pdf")
    assert len(text) > 100
    assert "PUTUSAN" in text

def test_detect_ocr_requirement():
    """Test detecting if OCR is needed"""
    # Searchable PDF
    needs_ocr = should_use_ocr("tests/fixtures/searchable.pdf")
    assert needs_ocr is False

    # Scanned PDF
    needs_ocr = should_use_ocr("tests/fixtures/scanned.pdf")
    assert needs_ocr is True

def test_ocr_scanned_document():
    """Test OCR on scanned document"""
    text = extract_with_ocr(
        "tests/fixtures/scanned.pdf",
        language="ind"
    )
    assert len(text) > 100
    assert "Terdakwa" in text

def test_handle_corrupted_pdf():
    """Test handling corrupted PDF"""
    with pytest.raises(PDFExtractionError):
        extract_pdf_text("tests/fixtures/corrupted.pdf")

def test_extract_metadata():
    """Test extracting PDF metadata"""
    metadata = extract_pdf_metadata("tests/fixtures/sample.pdf")
    assert "page_count" in metadata
    assert "file_size" in metadata
    assert metadata["page_count"] > 0
```

---

## 6. Text Normalization

### Task 6.1: Normalization Rules Engine

**Actionable Items:**
- [ ] Implement normalization rules processor
- [ ] Support regex-based replacements
- [ ] Support string-based replacements
- [ ] Implement rule priority ordering
- [ ] Add language-specific normalization
- [ ] Implement legal term standardization
- [ ] Add date normalization
- [ ] Add currency normalization
- [ ] Cache normalization results

**Positive Cases:**
- Apply single normalization rule
- Apply multiple rules in priority order
- Normalize legal terms (Terdakwa, Jaksa)
- Normalize dates (Indonesian to ISO)
- Normalize currency (Rp. 1.000.000 � 1000000)
- Handle section-specific rules

**Negative Cases:**
- Skip inactive rules
- Handle invalid regex patterns
- Handle null text input
- Handle empty rules list

**Edge Cases:**
- Rule with empty replacement string
- Rule that matches entire text
- Overlapping rule patterns
- Rule with capture groups
- Very long text (>1MB)

**Unit Tests:**
```python
def test_apply_single_rule():
    """Test applying single normalization rule"""
    rule = NormalizationRule(
        pattern="terdakwa",
        replacement="Terdakwa",
        is_regex=False
    )

    text = "bahwa terdakwa telah melakukan"
    result = apply_rule(text, rule)
    assert result == "bahwa Terdakwa telah melakukan"

def test_apply_regex_rule():
    """Test applying regex normalization rule"""
    rule = NormalizationRule(
        pattern=r"Rp\.?\s*(\d+)",
        replacement=r"\1",
        is_regex=True
    )

    text = "denda sebesar Rp. 1000000"
    result = apply_rule(text, rule)
    assert result == "denda sebesar 1000000"

def test_apply_multiple_rules_priority():
    """Test applying multiple rules in priority order"""
    rules = [
        NormalizationRule(pattern="JAKSA", replacement="Jaksa", priority=100),
        NormalizationRule(pattern="jaksa", replacement="Jaksa", priority=90),
    ]

    text = "JAKSA dan jaksa"
    result = apply_rules(text, rules)
    assert result == "Jaksa dan Jaksa"

def test_skip_inactive_rules():
    """Test skipping inactive rules"""
    rules = [
        NormalizationRule(pattern="test", replacement="TEST", is_active=True),
        NormalizationRule(pattern="skip", replacement="SKIP", is_active=False),
    ]

    text = "test skip"
    result = apply_rules(text, rules)
    assert result == "TEST skip"

def test_section_specific_rules():
    """Test applying rules to specific sections only"""
    rule = NormalizationRule(
        pattern="Pasal",
        replacement="PASAL",
        apply_to_sections=["DAKWAAN"]
    )

    # Should apply to DAKWAAN section
    text = "Pasal 2 ayat 1"
    result = apply_rule(text, rule, section="DAKWAAN")
    assert result == "PASAL 2 ayat 1"

    # Should not apply to other sections
    result = apply_rule(text, rule, section="PERTIMBANGAN")
    assert result == "Pasal 2 ayat 1"
```

---

## 7. Monitoring and Logging

### Task 7.1: Metrics and Observability

**Actionable Items:**
- [ ] Set up Prometheus metrics collection
- [ ] Define custom metrics for job processing
- [ ] Define custom metrics for extraction accuracy
- [ ] Define custom metrics for cost tracking
- [ ] Implement structured logging with context
- [ ] Add distributed tracing with job_id
- [ ] Create Grafana dashboards
- [ ] Set up alerting rules

**Positive Cases:**
- Record job processing time metric
- Record extraction cost metric
- Record field confidence metric
- Log job state transitions
- Track API request metrics
- Monitor queue depth

**Negative Cases:**
- Handle metrics collection failure gracefully
- Handle logging errors without breaking app
- Missing metric labels (use defaults)

**Edge Cases:**
- Very high metric cardinality
- Log message with sensitive data (redact)
- Metrics during service shutdown

**Unit Tests:**
```python
def test_record_job_duration_metric():
    """Test recording job processing duration"""
    metrics = MetricsCollector()

    with metrics.track_duration("job_processing", source_id="ID_SC"):
        time.sleep(0.1)

    duration = metrics.get_histogram("job_processing")
    assert duration > 0.1

def test_record_cost_metric():
    """Test recording cost metrics"""
    metrics = MetricsCollector()

    metrics.record_cost(
        source_id="ID_SC",
        cost_type="llm",
        amount=1.25
    )

    total = metrics.get_counter("total_cost")
    assert total == 1.25

def test_structured_logging_with_context():
    """Test structured logging with context"""
    logger = StructuredLogger()

    with logger.context(job_id="test-123", source_id="ID_SC"):
        logger.info("Processing started")

    # Verify log has context
    logs = get_logs()
    assert logs[-1]["job_id"] == "test-123"
    assert logs[-1]["source_id"] == "ID_SC"
```

---

## 8. Error Handling and Recovery

### Task 8.1: Comprehensive Error Handling

**Actionable Items:**
- [ ] Define custom exception hierarchy
- [ ] Implement retry logic with exponential backoff
- [ ] Add circuit breaker for external services
- [ ] Implement graceful degradation
- [ ] Add error classification (transient vs permanent)
- [ ] Implement dead letter queue handling
- [ ] Add error reporting and alerting
- [ ] Create error recovery procedures

**Positive Cases:**
- Retry transient errors (network timeout)
- Circuit breaker opens after threshold failures
- Graceful degradation when service unavailable
- Error properly logged and classified
- Failed job moved to DLQ after max retries

**Negative Cases:**
- Permanent error (no retry)
- Circuit breaker prevents cascading failures
- Service timeout with proper cleanup
- Invalid data error with helpful message

**Edge Cases:**
- Error during error handling
- Multiple concurrent errors
- Error during shutdown
- Partial failure (some fields extracted)

**Unit Tests:**
```python
def test_retry_transient_error():
    """Test retrying transient errors"""
    mock_service = Mock(side_effect=[
        ConnectionError("Timeout"),
        ConnectionError("Timeout"),
        {"result": "success"}
    ])

    result = retry_with_backoff(mock_service, max_retries=3)
    assert result["result"] == "success"
    assert mock_service.call_count == 3

def test_circuit_breaker():
    """Test circuit breaker pattern"""
    breaker = CircuitBreaker(threshold=3, timeout=60)
    mock_service = Mock(side_effect=Exception("Service down"))

    # Fail 3 times
    for _ in range(3):
        with pytest.raises(Exception):
            breaker.call(mock_service)

    # Circuit should be open
    assert breaker.is_open is True

    # Further calls should fail fast
    with pytest.raises(CircuitBreakerOpen):
        breaker.call(mock_service)

def test_error_classification():
    """Test classifying errors as transient or permanent"""
    assert is_transient_error(ConnectionError()) is True
    assert is_transient_error(TimeoutError()) is True
    assert is_transient_error(ValueError("Invalid data")) is False
    assert is_transient_error(FileNotFoundError()) is False
```

---

## Summary

**Total Tasks:** 17 major tasks (9 setup + 8 core functionality)

**Technology Stack:**
- **Python:** 3.14
- **Package Manager:** UV (not Poetry)
- **Web Framework:** FastAPI
- **Database:** PostgreSQL 16+
- **Migrations:** Alembic
- **SQL:** SQLC for type-safe queries
- **Testing:** pytest with async support
- **Containerization:** Docker with multi-stage builds
- **CI/CD:** GitHub Actions

**Priority Order:**
1. **Project Setup (Tasks 0.1-0.9)** - Foundation
   - UV and Python 3.14 setup
   - FastAPI application structure
   - Database with Alembic
   - SQLC for type-safe SQL
   - Docker & Docker Compose
   - OpenAPI contract generation
   - Test suite with pytest
   - GitHub Actions CI/CD
   - Development tools and scripts

2. **Database Schema (Task 1)** - Data foundation
3. **Configuration Management API (Task 2)** - Core functionality
4. **Field Management API (Task 3)** - Configuration
5. **Job Processing Infrastructure (Task 4)** - Essential for processing
6. **PDF Processing Pipeline (Task 5)** - Document handling
7. **Text Normalization (Task 6)** - Data quality
8. **Monitoring and Logging (Task 7)** - Observability
9. **Error Handling (Task 8)** - Reliability

**Estimated Timeline:**
- Phase 0 (Project Setup): 1 week
- Phase 1 (Tasks 1-3): 2 weeks
- Phase 2 (Tasks 4-6): 3 weeks
- Phase 3 (Tasks 7-8): 1 week

**Dependencies:**
- All core tasks depend on Task 0 (Project setup)
- Task 2-3 depend on Task 1 (DB schema)
- Task 4 depends on Task 1-2 (DB + API)
- Task 5-6 can be parallel with Task 3-4
- Task 7-8 should be ongoing throughout

**Primary Developer Interface: Make Commands**

All development tasks should use Make as the primary interface:

| Command | Description | Underlying UV Command |
|---------|-------------|----------------------|
| `make help` | Show all available targets | - |
| `make install` | Install dependencies | `uv sync` |
| `make dev` | Run development server | `uv run uvicorn ...` |
| `make test` | Run all tests | `uv run pytest` |
| `make test-cov` | Run tests with coverage | `uv run pytest --cov` |
| `make lint` | Run linter | `uv run ruff check` |
| `make format` | Format code | `uv run ruff format` |
| `make typecheck` | Run type checker | `uv run mypy` |
| `make check` | Run all checks | lint + typecheck + test |
| `make migrate` | Apply migrations | `uv run alembic upgrade head` |
| `make migrate-down` | Rollback migration | `uv run alembic downgrade -1` |
| `make migration` | Create new migration | `uv run alembic revision --autogenerate` |
| `make db-reset` | Reset database | Drop + create + migrate |
| `make db-seed` | Seed test data | Custom script |
| `make docker-build` | Build Docker image | `docker build` |
| `make docker-up` | Start all services | `docker-compose up` |
| `make docker-down` | Stop all services | `docker-compose down` |
| `make openapi` | Generate OpenAPI spec | FastAPI export |
| `make sqlc-generate` | Generate SQLC code | `sqlc generate` |
| `make clean` | Clean build artifacts | Remove __pycache__, .pytest_cache, etc. |

**Direct UV Commands (for reference):**
- `uv sync` - Install dependencies
- `uv run <command>` - Run commands in virtual environment
- `uv add <package>` - Add dependency
- `uv remove <package>` - Remove dependency

**Typical Development Workflow:**
```bash
# Initial setup
make install              # Install dependencies
make docker-up            # Start PostgreSQL, Redis, etc.
make migrate              # Apply database migrations
make db-seed              # Load test data

# Development
make dev                  # Start development server (hot reload enabled)

# Before committing
make format               # Format code
make check                # Run all checks (lint, typecheck, test)

# Database changes
make migration            # Create new migration
make migrate              # Apply migration
make migrate-down         # Rollback if needed

# Testing
make test                 # Run all tests
make test-cov             # Generate coverage report

# Cleanup
make docker-down          # Stop all services
make clean                # Clean artifacts
```

**Testing Coverage Target:** >90% for all modules

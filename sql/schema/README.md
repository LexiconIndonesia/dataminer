# SQL Schema for SQLC

This directory contains the database schema files used by SQLC for type-safe code generation.

## Files

- `current_schema.sql` - Auto-generated schema snapshot from the database

## Important Notes

- The `current_schema.sql` file is **auto-generated** from the database and should **not be edited manually**
- This file is committed to git so CI can generate SQLC code without a running database
- After creating new migrations, regenerate this file using `make schema-generate`

## Workflow

1. Create migration files in `migrations/alembic/versions/`
2. Apply migrations to the database: `make migrate`
3. Regenerate the schema snapshot: `make schema-generate`
4. Generate SQLC code: `make sqlc-generate`
5. Commit both the migration and the updated schema file together

Or use the shortcut after migrations:
```bash
make regenerate-all  # Runs schema-generate + sqlc-generate
```

## Conceptual Model

Think of it like Git:
- **Migrations** = Git commits (history of changes)
- **Schema** = Current HEAD (latest state)

SQLC uses the schema files to generate type-safe Python code, while Alembic migrations handle the actual database evolution.

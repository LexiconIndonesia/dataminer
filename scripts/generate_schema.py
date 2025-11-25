#!/usr/bin/env python3
"""Generate SQL schema file from Alembic migrations.

This script applies all Alembic migrations to generate a complete SQL schema
which can then be used by SQLC for code generation.

Note: This requires a temporary database to apply migrations.
"""

import subprocess
import sys
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))


def generate_schema_sql(output_file: str = "sql/schema/current_schema.sql") -> None:
    """Generate schema SQL file from Alembic migrations."""
    print("Generating schema from Alembic migrations...")

    # Get database URL from settings
    from dataminer.core.config import get_settings

    settings = get_settings()
    db_url = str(settings.database_url)

    # Create temporary database for schema extraction
    from urllib.parse import urlparse, urlunparse

    import psycopg2
    from psycopg2 import sql

    parsed = urlparse(db_url)

    # Generate unique database name safe for PostgreSQL identifiers
    # Format: temp_schema_YYYYMMDD_HHMMSS_<uuid_short>
    # Example: temp_schema_20251124_153045_a1b2c3d4e5f6
    #
    # Safety guarantees:
    # - Characters: lowercase letters, digits, underscores only (PostgreSQL safe)
    # - Length: ~40 chars (well under PostgreSQL's 63 char limit)
    # - Starts with letter (required by PostgreSQL)
    # - Uniqueness: timestamp (second precision) + UUID hex (cryptographic randomness)
    # - No collision risk across concurrent runs
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    unique_id = uuid4().hex[:12]  # Use first 12 chars of UUID for uniqueness
    temp_db_name = f"temp_schema_{timestamp}_{unique_id}"

    # Initialize connection and cursor for proper cleanup
    conn = None
    cursor = None

    try:
        # Connect to default database to create temp database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database="postgres",
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Create temp database
        # Use sql.Identifier to safely quote database name (prevents SQL injection)
        cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(temp_db_name)))
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(temp_db_name)))
        print(f"✓ Created temporary database: {temp_db_name}")

        # Update database URL to use temp database
        # Use _replace to properly update only the path component
        temp_parsed = parsed._replace(path=f"/{temp_db_name}")
        temp_url = urlunparse(temp_parsed)

        # Run Alembic migrations on temp database
        import os

        env = os.environ.copy()
        env["DATABASE_URL"] = temp_url

        try:
            subprocess.run(
                ["uv", "run", "alembic", "upgrade", "head"],
                check=True,
                env=env,
                capture_output=True,
                text=True,
            )
            print("✓ Applied all migrations")
        except subprocess.CalledProcessError as e:
            print("Error running Alembic migrations:")
            if e.stdout:
                print(f"STDOUT:\n{e.stdout}")
            if e.stderr:
                print(f"STDERR:\n{e.stderr}")
            sys.exit(1)

        # Extract schema using pg_dump via Docker
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Use pg_dump from Docker container since it may not be installed locally
        # The container name is 'dataminer-postgres' from docker-compose.yml
        dump_process = subprocess.run(
            [
                "docker",
                "exec",
                "dataminer-postgres",
                "pg_dump",
                "--username",
                parsed.username or "postgres",
                "--schema-only",
                "--no-owner",
                "--no-privileges",
                temp_db_name,
            ],
            capture_output=True,
            text=True,
            env=os.environ.copy(),
        )

        if dump_process.returncode != 0:
            print("Error running pg_dump:")
            if dump_process.stdout:
                print(f"STDOUT:\n{dump_process.stdout}")
            if dump_process.stderr:
                print(f"STDERR:\n{dump_process.stderr}")
            sys.exit(1)

        # Clean up pg_dump output for SQLC compatibility
        schema_sql = dump_process.stdout

        # Remove PostgreSQL-specific commands that SQLC can't parse
        import re

        # Remove \restrict and similar backslash commands
        schema_sql = re.sub(r"^\\[a-z]+.*$", "", schema_sql, flags=re.MULTILINE)

        # Remove empty lines at the start
        schema_sql = schema_sql.lstrip("\n")

        # Write schema to file with header
        with output_path.open("w") as f:
            f.write("-- Schema for dataminer database\n")
            f.write("-- Auto-generated from Alembic migrations\n")
            f.write("-- DO NOT EDIT MANUALLY - Use 'make schema-generate' to regenerate\n\n")
            f.write(schema_sql)

        print(f"✓ Schema SQL generated: {output_path}")

    finally:
        # Cleanup: drop temp database and close connections
        if cursor is not None:
            try:
                # Use sql.Identifier to safely quote database name (prevents SQL injection)
                cursor.execute(
                    sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(temp_db_name))
                )
            except Exception as e:
                # Best effort cleanup - don't fail if database doesn't exist
                print(f"Warning: Could not drop temp database: {e}")
            with suppress(Exception):
                cursor.close()

        if conn is not None:
            with suppress(Exception):
                conn.close()

        print("✓ Cleaned up temporary database")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate SQL schema from Alembic migrations")
    parser.add_argument(
        "--output",
        "-o",
        default="sql/schema/current_schema.sql",
        help="Output file path (default: sql/schema/current_schema.sql)",
    )

    args = parser.parse_args()
    generate_schema_sql(args.output)

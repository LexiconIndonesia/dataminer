#!/usr/bin/env python3
"""Generate SQL schema file from Alembic migrations.

This script uses Alembic's offline mode to generate a complete SQL schema
from all migrations, which can then be used by SQLC for code generation.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))


def generate_schema_sql(output_file: str = "sql/schema.sql") -> None:
    """Generate schema SQL file from Alembic migrations."""
    # Import database URL
    from sqlalchemy import create_engine

    from dataminer.db.base import get_sync_engine_url

    # Create engine
    engine = create_engine(get_sync_engine_url())

    # Generate SQL schema from metadata
    from dataminer.db import models  # noqa: F401 - Import to register models
    from dataminer.db.base import Base

    # Create schema file header
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w") as f:
        f.write("-- Schema for dataminer database\n")
        f.write("-- Auto-generated from SQLAlchemy models\n")
        f.write("-- DO NOT EDIT MANUALLY - Use 'make schema-generate' to regenerate\n\n")

        # Use CreateTable to generate DDL
        from sqlalchemy.schema import CreateIndex, CreateTable

        for table in Base.metadata.sorted_tables:
            # Generate CREATE TABLE statement
            create_table = CreateTable(table, if_not_exists=True)
            ddl = str(create_table.compile(engine))
            f.write(ddl)
            f.write(";\n\n")

        # Generate indexes
        f.write("-- Indexes\n")
        for table in Base.metadata.sorted_tables:
            for index in table.indexes:
                create_index = CreateIndex(index, if_not_exists=True)
                ddl = str(create_index.compile(engine))
                f.write(ddl)
                f.write(";\n")

    print(f"✓ Schema SQL generated: {output_path}")
    print(f"✓ Generated {len(Base.metadata.sorted_tables)} tables")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate SQL schema from Alembic migrations")
    parser.add_argument(
        "--output",
        "-o",
        default="sql/schema.sql",
        help="Output file path (default: sql/schema.sql)",
    )

    args = parser.parse_args()
    generate_schema_sql(args.output)

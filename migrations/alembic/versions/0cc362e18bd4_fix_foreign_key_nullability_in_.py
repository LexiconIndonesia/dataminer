"""fix_foreign_key_nullability_in_configuration_tables

Revision ID: 0cc362e18bd4
Revises: f792da96c208
Create Date: 2025-11-24 15:55:05.353922

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0cc362e18bd4"
down_revision: str | Sequence[str] | None = "f792da96c208"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make source_id NOT NULL in all tables
    # Note: The unique constraints were created without explicit names in the first migration,
    # so PostgreSQL auto-generated names like "{table}_{columns}_key".
    # We drop the old indexes and constraints, then recreate them after making source_id NOT NULL.

    # source_extraction_profiles
    op.drop_index("idx_profiles_active", table_name="source_extraction_profiles")
    op.drop_index("idx_profiles_source", table_name="source_extraction_profiles")
    op.drop_constraint(
        "source_extraction_profiles_source_id_profile_name_key",
        "source_extraction_profiles",
        type_="unique",
    )
    op.alter_column(
        "source_extraction_profiles",
        "source_id",
        existing_type=sa.VARCHAR(length=20),
        nullable=False,
    )
    # Recreate constraints and indexes for source_extraction_profiles
    op.create_unique_constraint(
        "source_extraction_profiles_source_id_profile_name_key",
        "source_extraction_profiles",
        ["source_id", "profile_name"],
    )
    op.create_index(
        "idx_profiles_source",
        "source_extraction_profiles",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        "idx_profiles_active",
        "source_extraction_profiles",
        ["source_id", "is_active"],
        unique=False,
    )

    # source_field_definitions
    op.drop_index("idx_fields_category", table_name="source_field_definitions")
    op.drop_index("idx_fields_source", table_name="source_field_definitions")
    op.drop_constraint(
        "source_field_definitions_source_id_field_name_key",
        "source_field_definitions",
        type_="unique",
    )
    op.alter_column(
        "source_field_definitions",
        "source_id",
        existing_type=sa.VARCHAR(length=20),
        nullable=False,
    )
    # Recreate constraints and indexes for source_field_definitions
    op.create_unique_constraint(
        "source_field_definitions_source_id_field_name_key",
        "source_field_definitions",
        ["source_id", "field_name"],
    )
    op.create_index(
        "idx_fields_source",
        "source_field_definitions",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        "idx_fields_category",
        "source_field_definitions",
        ["source_id", "field_category"],
        unique=False,
    )

    # source_normalization_rules
    op.drop_index("idx_rules_source", table_name="source_normalization_rules")
    op.alter_column(
        "source_normalization_rules",
        "source_id",
        existing_type=sa.VARCHAR(length=20),
        nullable=False,
    )
    # Recreate index for source_normalization_rules
    op.create_index(
        "idx_rules_source",
        "source_normalization_rules",
        ["source_id", "is_active"],
        unique=False,
    )

    # source_prompt_templates
    op.drop_index("idx_templates_source", table_name="source_prompt_templates")
    op.drop_constraint(
        "source_prompt_templates_source_id_template_name_version_key",
        "source_prompt_templates",
        type_="unique",
    )
    op.alter_column(
        "source_prompt_templates",
        "source_id",
        existing_type=sa.VARCHAR(length=20),
        nullable=False,
    )
    # Recreate constraints and indexes for source_prompt_templates
    op.create_unique_constraint(
        "source_prompt_templates_source_id_template_name_version_key",
        "source_prompt_templates",
        ["source_id", "template_name", "version"],
    )
    op.create_index(
        "idx_templates_source",
        "source_prompt_templates",
        ["source_id", "is_active"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Restore source_prompt_templates
    # First drop the indexes and constraints created in upgrade
    op.drop_index("idx_templates_source", table_name="source_prompt_templates")
    op.drop_constraint(
        "source_prompt_templates_source_id_template_name_version_key",
        "source_prompt_templates",
        type_="unique",
    )
    op.alter_column(
        "source_prompt_templates",
        "source_id",
        existing_type=sa.VARCHAR(length=20),
        nullable=True,
    )
    # Recreate indexes and constraints
    op.create_unique_constraint(
        "source_prompt_templates_source_id_template_name_version_key",
        "source_prompt_templates",
        ["source_id", "template_name", "version"],
    )
    op.create_index(
        "idx_templates_source",
        "source_prompt_templates",
        ["source_id", "is_active"],
        unique=False,
    )

    # Restore source_normalization_rules
    # First drop the index created in upgrade
    op.drop_index("idx_rules_source", table_name="source_normalization_rules")
    op.alter_column(
        "source_normalization_rules",
        "source_id",
        existing_type=sa.VARCHAR(length=20),
        nullable=True,
    )
    # Recreate index
    op.create_index(
        "idx_rules_source",
        "source_normalization_rules",
        ["source_id", "is_active"],
        unique=False,
    )

    # Restore source_field_definitions
    # First drop the indexes and constraints created in upgrade
    op.drop_index("idx_fields_category", table_name="source_field_definitions")
    op.drop_index("idx_fields_source", table_name="source_field_definitions")
    op.drop_constraint(
        "source_field_definitions_source_id_field_name_key",
        "source_field_definitions",
        type_="unique",
    )
    op.alter_column(
        "source_field_definitions",
        "source_id",
        existing_type=sa.VARCHAR(length=20),
        nullable=True,
    )
    # Recreate indexes and constraints
    op.create_unique_constraint(
        "source_field_definitions_source_id_field_name_key",
        "source_field_definitions",
        ["source_id", "field_name"],
    )
    op.create_index(
        "idx_fields_source",
        "source_field_definitions",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        "idx_fields_category",
        "source_field_definitions",
        ["source_id", "field_category"],
        unique=False,
    )

    # Restore source_extraction_profiles
    # First drop the indexes and constraints created in upgrade
    op.drop_index("idx_profiles_active", table_name="source_extraction_profiles")
    op.drop_index("idx_profiles_source", table_name="source_extraction_profiles")
    op.drop_constraint(
        "source_extraction_profiles_source_id_profile_name_key",
        "source_extraction_profiles",
        type_="unique",
    )
    op.alter_column(
        "source_extraction_profiles",
        "source_id",
        existing_type=sa.VARCHAR(length=20),
        nullable=True,
    )
    # Recreate indexes and constraints
    op.create_unique_constraint(
        "source_extraction_profiles_source_id_profile_name_key",
        "source_extraction_profiles",
        ["source_id", "profile_name"],
    )
    op.create_index(
        "idx_profiles_source",
        "source_extraction_profiles",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        "idx_profiles_active",
        "source_extraction_profiles",
        ["source_id", "is_active"],
        unique=False,
    )

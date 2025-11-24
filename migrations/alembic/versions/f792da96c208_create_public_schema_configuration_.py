"""create_public_schema_configuration_tables

Revision ID: f792da96c208
Revises:
Create Date: 2025-11-24 15:11:42.661561

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f792da96c208"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create document_sources table
    op.create_table(
        "document_sources",
        sa.Column("source_id", sa.String(length=20), nullable=False),
        sa.Column("source_name", sa.String(length=200), nullable=False),
        sa.Column("country_code", sa.String(length=3), nullable=True),
        sa.Column("primary_language", sa.String(length=10), nullable=True),
        sa.Column("secondary_languages", sa.ARRAY(sa.String(length=10)), nullable=True),
        sa.Column("legal_system", sa.String(length=50), nullable=True),
        sa.Column("document_type", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=True),
        sa.Column("phase", sa.Integer(), server_default="1", nullable=True),
        sa.Column("total_documents_processed", sa.Integer(), server_default="0", nullable=True),
        sa.Column("avg_accuracy", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("avg_cost_per_document", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("NOW()"), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("NOW()"), nullable=True),
        sa.PrimaryKeyConstraint("source_id"),
    )

    # Create source_extraction_profiles table
    op.create_table(
        "source_extraction_profiles",
        sa.Column(
            "profile_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("source_id", sa.String(length=20), nullable=True),
        sa.Column("profile_name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=True),
        sa.Column("is_default", sa.Boolean(), server_default="false", nullable=True),
        sa.Column(
            "pdf_extraction_method",
            sa.String(length=50),
            server_default="pdfplumber",
            nullable=True,
        ),
        sa.Column(
            "ocr_threshold", sa.Numeric(precision=3, scale=2), server_default="0.80", nullable=True
        ),
        sa.Column("ocr_language", sa.String(length=10), nullable=True),
        sa.Column("use_document_ai_fallback", sa.Boolean(), server_default="true", nullable=True),
        sa.Column(
            "segmentation_method",
            sa.String(length=50),
            server_default="section_based",
            nullable=True,
        ),
        sa.Column("segment_size_tokens", sa.Integer(), server_default="3000", nullable=True),
        sa.Column("segment_overlap_tokens", sa.Integer(), server_default="200", nullable=True),
        sa.Column(
            "llm_model_quick",
            sa.String(length=50),
            server_default="gemini-1.5-flash",
            nullable=True,
        ),
        sa.Column(
            "llm_model_detailed",
            sa.String(length=50),
            server_default="gemini-1.5-pro",
            nullable=True,
        ),
        sa.Column(
            "llm_temperature", sa.Numeric(precision=2, scale=1), server_default="0.1", nullable=True
        ),
        sa.Column("max_retries", sa.Integer(), server_default="2", nullable=True),
        sa.Column(
            "max_cost_per_document",
            sa.Numeric(precision=10, scale=2),
            server_default="2.00",
            nullable=True,
        ),
        sa.Column("enable_deep_dive_pass", sa.Boolean(), server_default="true", nullable=True),
        sa.Column(
            "deep_dive_confidence_threshold",
            sa.Numeric(precision=3, scale=2),
            server_default="0.75",
            nullable=True,
        ),
        sa.Column("version", sa.Integer(), server_default="1", nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("NOW()"), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("NOW()"), nullable=True),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["document_sources.source_id"],
        ),
        sa.PrimaryKeyConstraint("profile_id"),
        sa.UniqueConstraint("source_id", "profile_name"),
    )

    # Create source_field_definitions table
    op.create_table(
        "source_field_definitions",
        sa.Column(
            "field_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("source_id", sa.String(length=20), nullable=True),
        sa.Column("field_name", sa.String(length=100), nullable=False),
        sa.Column("field_display_name", sa.String(length=200), nullable=True),
        sa.Column("field_category", sa.String(length=50), nullable=True),
        sa.Column("field_type", sa.String(length=50), nullable=True),
        sa.Column("extraction_method", sa.String(length=50), nullable=True),
        sa.Column("extraction_section", sa.String(length=100), nullable=True),
        sa.Column("regex_pattern", sa.Text(), nullable=True),
        sa.Column("llm_prompt_template_id", sa.UUID(), nullable=True),
        sa.Column("is_required", sa.Boolean(), server_default="false", nullable=True),
        sa.Column("validation_rules", sa.JSON(), nullable=True),
        sa.Column(
            "confidence_threshold",
            sa.Numeric(precision=3, scale=2),
            server_default="0.75",
            nullable=True,
        ),
        sa.Column("normalization_rules", sa.JSON(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("NOW()"), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("NOW()"), nullable=True),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["document_sources.source_id"],
        ),
        sa.PrimaryKeyConstraint("field_id"),
        sa.UniqueConstraint("source_id", "field_name"),
    )

    # Create source_normalization_rules table
    op.create_table(
        "source_normalization_rules",
        sa.Column(
            "rule_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("source_id", sa.String(length=20), nullable=True),
        sa.Column("rule_name", sa.String(length=100), nullable=False),
        sa.Column("rule_type", sa.String(length=50), nullable=True),
        sa.Column("pattern", sa.Text(), nullable=False),
        sa.Column("replacement", sa.Text(), nullable=True),
        sa.Column("is_regex", sa.Boolean(), server_default="false", nullable=True),
        sa.Column("apply_to_sections", sa.ARRAY(sa.String(length=100)), nullable=True),
        sa.Column("priority", sa.Integer(), server_default="100", nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("NOW()"), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("NOW()"), nullable=True),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["document_sources.source_id"],
        ),
        sa.PrimaryKeyConstraint("rule_id"),
    )

    # Create source_prompt_templates table
    op.create_table(
        "source_prompt_templates",
        sa.Column(
            "template_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("source_id", sa.String(length=20), nullable=True),
        sa.Column("template_name", sa.String(length=100), nullable=False),
        sa.Column("template_type", sa.String(length=50), nullable=True),
        sa.Column("language_code", sa.String(length=10), nullable=True),
        sa.Column("prompt_text", sa.Text(), nullable=False),
        sa.Column("variables", sa.JSON(), nullable=True),
        sa.Column("usage_count", sa.Integer(), server_default="0", nullable=True),
        sa.Column("avg_confidence", sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column("avg_tokens_used", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("NOW()"), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("NOW()"), nullable=True),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["document_sources.source_id"],
        ),
        sa.PrimaryKeyConstraint("template_id"),
        sa.UniqueConstraint("source_id", "template_name", "version"),
    )

    # Create indexes for performance
    op.create_index(
        "idx_profiles_source", "source_extraction_profiles", ["source_id"], unique=False
    )
    op.create_index(
        "idx_profiles_active",
        "source_extraction_profiles",
        ["source_id", "is_active"],
        unique=False,
    )
    op.create_index("idx_fields_source", "source_field_definitions", ["source_id"], unique=False)
    op.create_index(
        "idx_fields_category",
        "source_field_definitions",
        ["source_id", "field_category"],
        unique=False,
    )
    op.create_index(
        "idx_rules_source", "source_normalization_rules", ["source_id", "is_active"], unique=False
    )
    op.create_index(
        "idx_templates_source", "source_prompt_templates", ["source_id", "is_active"], unique=False
    )

    # Insert initial ID_SC source
    op.execute("""
        INSERT INTO document_sources (source_id, source_name, country_code, primary_language, legal_system, document_type, phase)
        VALUES ('ID_SC', 'Indonesian Supreme Court', 'IDN', 'id', 'civil_law', 'court_judgment', 1)
        ON CONFLICT (source_id) DO NOTHING
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index("idx_templates_source", table_name="source_prompt_templates")
    op.drop_index("idx_rules_source", table_name="source_normalization_rules")
    op.drop_index("idx_fields_category", table_name="source_field_definitions")
    op.drop_index("idx_fields_source", table_name="source_field_definitions")
    op.drop_index("idx_profiles_active", table_name="source_extraction_profiles")
    op.drop_index("idx_profiles_source", table_name="source_extraction_profiles")

    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table("source_prompt_templates")
    op.drop_table("source_normalization_rules")
    op.drop_table("source_field_definitions")
    op.drop_table("source_extraction_profiles")
    op.drop_table("document_sources")

"""add_column_comments

Revision ID: 66703a7a9dba
Revises: 0cc362e18bd4
Create Date: 2025-11-25 11:46:28.466175

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "66703a7a9dba"
down_revision: str | Sequence[str] | None = "0cc362e18bd4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add comments to all columns for documentation."""
    # ===================
    # document_sources
    # ===================
    op.execute(
        "COMMENT ON TABLE document_sources IS 'Master table for document sources (courts, agencies, etc.)'"
    )
    op.execute(
        "COMMENT ON COLUMN document_sources.source_id IS 'Unique identifier for the source (e.g., ID_SC for Indonesian Supreme Court)'"
    )
    op.execute(
        "COMMENT ON COLUMN document_sources.source_name IS 'Human-readable name of the document source'"
    )
    op.execute(
        "COMMENT ON COLUMN document_sources.country_code IS 'ISO 3166-1 alpha-3 country code (e.g., IDN, USA, GBR)'"
    )
    op.execute(
        "COMMENT ON COLUMN document_sources.primary_language IS 'Primary language code (ISO 639-1, e.g., id, en)'"
    )
    op.execute(
        "COMMENT ON COLUMN document_sources.secondary_languages IS 'Array of secondary language codes used in documents'"
    )
    op.execute(
        "COMMENT ON COLUMN document_sources.legal_system IS 'Type of legal system (civil_law, common_law, mixed, religious)'"
    )
    op.execute(
        "COMMENT ON COLUMN document_sources.document_type IS 'Type of documents from this source (court_judgment, legislation, contract)'"
    )
    op.execute(
        "COMMENT ON COLUMN document_sources.is_active IS 'Whether this source is currently active for processing'"
    )
    op.execute(
        "COMMENT ON COLUMN document_sources.phase IS 'Current processing phase (1=initial, 2=expanded, 3=full)'"
    )
    op.execute(
        "COMMENT ON COLUMN document_sources.total_documents_processed IS 'Running count of documents processed from this source'"
    )
    op.execute(
        "COMMENT ON COLUMN document_sources.avg_accuracy IS 'Average extraction accuracy score (0.00-1.00)'"
    )
    op.execute(
        "COMMENT ON COLUMN document_sources.avg_cost_per_document IS 'Average processing cost per document in USD'"
    )
    op.execute(
        "COMMENT ON COLUMN document_sources.created_at IS 'Timestamp when record was created'"
    )
    op.execute(
        "COMMENT ON COLUMN document_sources.updated_at IS 'Timestamp when record was last updated'"
    )

    # =============================
    # source_extraction_profiles
    # =============================
    op.execute(
        "COMMENT ON TABLE source_extraction_profiles IS 'Extraction configuration profiles for each document source'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.profile_id IS 'Unique identifier for the profile (UUID)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.source_id IS 'Reference to the document source this profile belongs to'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.profile_name IS 'Human-readable name for this profile'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.is_active IS 'Whether this profile is currently active'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.is_default IS 'Whether this is the default profile for the source'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.pdf_extraction_method IS 'PDF text extraction method (pdfplumber, pypdf2, pdfminer)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.ocr_threshold IS 'Text density threshold below which OCR is triggered (0.00-1.00)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.ocr_language IS 'Language code for OCR processing'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.use_document_ai_fallback IS 'Whether to use Document AI as fallback for failed extractions'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.segmentation_method IS 'Document segmentation method (section_based, fixed_size, semantic)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.segment_size_tokens IS 'Target size of each segment in tokens'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.segment_overlap_tokens IS 'Number of overlapping tokens between segments'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.llm_model_quick IS 'LLM model for quick/initial extraction passes'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.llm_model_detailed IS 'LLM model for detailed/deep extraction passes'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.llm_temperature IS 'Temperature setting for LLM inference (0.0-1.0)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.max_retries IS 'Maximum retry attempts for failed extractions'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.max_cost_per_document IS 'Maximum allowed cost per document in USD'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.enable_deep_dive_pass IS 'Whether to enable deep dive extraction pass for low-confidence fields'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.deep_dive_confidence_threshold IS 'Confidence threshold below which deep dive is triggered (0.00-1.00)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.version IS 'Version number of this profile configuration'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.created_at IS 'Timestamp when record was created'"
    )
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.updated_at IS 'Timestamp when record was last updated'"
    )

    # ==========================
    # source_field_definitions
    # ==========================
    op.execute(
        "COMMENT ON TABLE source_field_definitions IS 'Field definitions for data extraction from each source'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.field_id IS 'Unique identifier for the field (UUID)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.source_id IS 'Reference to the document source this field belongs to'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.field_name IS 'Internal field name (snake_case, e.g., case_number)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.field_display_name IS 'Human-readable display name for the field'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.field_category IS 'Category grouping (metadata, parties, decision, dates)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.field_type IS 'Data type (string, date, number, array, object)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.extraction_method IS 'How to extract this field (regex, llm, hybrid, rule_based)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.extraction_section IS 'Document section to search for this field'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.regex_pattern IS 'Regular expression pattern for regex extraction'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.llm_prompt_template_id IS 'Reference to prompt template for LLM extraction'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.is_required IS 'Whether this field is required for valid extraction'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.validation_rules IS 'JSON object with validation rules for the field'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.confidence_threshold IS 'Minimum confidence score to accept extraction (0.00-1.00)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.normalization_rules IS 'JSON object with normalization/transformation rules'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.display_order IS 'Order in which to display this field in UI'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.created_at IS 'Timestamp when record was created'"
    )
    op.execute(
        "COMMENT ON COLUMN source_field_definitions.updated_at IS 'Timestamp when record was last updated'"
    )

    # ============================
    # source_normalization_rules
    # ============================
    op.execute(
        "COMMENT ON TABLE source_normalization_rules IS 'Text normalization rules for cleaning extracted content'"
    )
    op.execute(
        "COMMENT ON COLUMN source_normalization_rules.rule_id IS 'Unique identifier for the rule (UUID)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_normalization_rules.source_id IS 'Reference to the document source this rule belongs to'"
    )
    op.execute(
        "COMMENT ON COLUMN source_normalization_rules.rule_name IS 'Human-readable name for this rule'"
    )
    op.execute(
        "COMMENT ON COLUMN source_normalization_rules.rule_type IS 'Type of normalization (whitespace, unicode, case, custom)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_normalization_rules.pattern IS 'Pattern to match (string or regex based on is_regex)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_normalization_rules.replacement IS 'Replacement text for matched pattern'"
    )
    op.execute(
        "COMMENT ON COLUMN source_normalization_rules.is_regex IS 'Whether pattern is a regular expression'"
    )
    op.execute(
        "COMMENT ON COLUMN source_normalization_rules.apply_to_sections IS 'Array of section names where this rule applies'"
    )
    op.execute(
        "COMMENT ON COLUMN source_normalization_rules.priority IS 'Execution priority (lower numbers run first)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_normalization_rules.is_active IS 'Whether this rule is currently active'"
    )
    op.execute(
        "COMMENT ON COLUMN source_normalization_rules.created_at IS 'Timestamp when record was created'"
    )
    op.execute(
        "COMMENT ON COLUMN source_normalization_rules.updated_at IS 'Timestamp when record was last updated'"
    )

    # =========================
    # source_prompt_templates
    # =========================
    op.execute(
        "COMMENT ON TABLE source_prompt_templates IS 'LLM prompt templates for field extraction'"
    )
    op.execute(
        "COMMENT ON COLUMN source_prompt_templates.template_id IS 'Unique identifier for the template (UUID)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_prompt_templates.source_id IS 'Reference to the document source this template belongs to'"
    )
    op.execute(
        "COMMENT ON COLUMN source_prompt_templates.template_name IS 'Human-readable name for this template'"
    )
    op.execute(
        "COMMENT ON COLUMN source_prompt_templates.template_type IS 'Type of prompt (extraction, validation, summarization)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_prompt_templates.language_code IS 'Language code for this template (for multi-language support)'"
    )
    op.execute(
        "COMMENT ON COLUMN source_prompt_templates.prompt_text IS 'The actual prompt template text'"
    )
    op.execute(
        "COMMENT ON COLUMN source_prompt_templates.variables IS 'JSON array of variable names used in the template'"
    )
    op.execute(
        "COMMENT ON COLUMN source_prompt_templates.usage_count IS 'Number of times this template has been used'"
    )
    op.execute(
        "COMMENT ON COLUMN source_prompt_templates.avg_confidence IS 'Average confidence score from extractions using this template'"
    )
    op.execute(
        "COMMENT ON COLUMN source_prompt_templates.avg_tokens_used IS 'Average tokens consumed per use'"
    )
    op.execute(
        "COMMENT ON COLUMN source_prompt_templates.is_active IS 'Whether this template is currently active'"
    )
    op.execute(
        "COMMENT ON COLUMN source_prompt_templates.version IS 'Version number of this template'"
    )
    op.execute(
        "COMMENT ON COLUMN source_prompt_templates.created_at IS 'Timestamp when record was created'"
    )
    op.execute(
        "COMMENT ON COLUMN source_prompt_templates.updated_at IS 'Timestamp when record was last updated'"
    )


def downgrade() -> None:
    """Remove all column comments."""
    # document_sources
    op.execute("COMMENT ON TABLE document_sources IS NULL")
    op.execute("COMMENT ON COLUMN document_sources.source_id IS NULL")
    op.execute("COMMENT ON COLUMN document_sources.source_name IS NULL")
    op.execute("COMMENT ON COLUMN document_sources.country_code IS NULL")
    op.execute("COMMENT ON COLUMN document_sources.primary_language IS NULL")
    op.execute("COMMENT ON COLUMN document_sources.secondary_languages IS NULL")
    op.execute("COMMENT ON COLUMN document_sources.legal_system IS NULL")
    op.execute("COMMENT ON COLUMN document_sources.document_type IS NULL")
    op.execute("COMMENT ON COLUMN document_sources.is_active IS NULL")
    op.execute("COMMENT ON COLUMN document_sources.phase IS NULL")
    op.execute("COMMENT ON COLUMN document_sources.total_documents_processed IS NULL")
    op.execute("COMMENT ON COLUMN document_sources.avg_accuracy IS NULL")
    op.execute("COMMENT ON COLUMN document_sources.avg_cost_per_document IS NULL")
    op.execute("COMMENT ON COLUMN document_sources.created_at IS NULL")
    op.execute("COMMENT ON COLUMN document_sources.updated_at IS NULL")

    # source_extraction_profiles
    op.execute("COMMENT ON TABLE source_extraction_profiles IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.profile_id IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.source_id IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.profile_name IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.is_active IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.is_default IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.pdf_extraction_method IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.ocr_threshold IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.ocr_language IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.use_document_ai_fallback IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.segmentation_method IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.segment_size_tokens IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.segment_overlap_tokens IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.llm_model_quick IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.llm_model_detailed IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.llm_temperature IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.max_retries IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.max_cost_per_document IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.enable_deep_dive_pass IS NULL")
    op.execute(
        "COMMENT ON COLUMN source_extraction_profiles.deep_dive_confidence_threshold IS NULL"
    )
    op.execute("COMMENT ON COLUMN source_extraction_profiles.version IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.created_at IS NULL")
    op.execute("COMMENT ON COLUMN source_extraction_profiles.updated_at IS NULL")

    # source_field_definitions
    op.execute("COMMENT ON TABLE source_field_definitions IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.field_id IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.source_id IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.field_name IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.field_display_name IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.field_category IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.field_type IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.extraction_method IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.extraction_section IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.regex_pattern IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.llm_prompt_template_id IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.is_required IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.validation_rules IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.confidence_threshold IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.normalization_rules IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.display_order IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.created_at IS NULL")
    op.execute("COMMENT ON COLUMN source_field_definitions.updated_at IS NULL")

    # source_normalization_rules
    op.execute("COMMENT ON TABLE source_normalization_rules IS NULL")
    op.execute("COMMENT ON COLUMN source_normalization_rules.rule_id IS NULL")
    op.execute("COMMENT ON COLUMN source_normalization_rules.source_id IS NULL")
    op.execute("COMMENT ON COLUMN source_normalization_rules.rule_name IS NULL")
    op.execute("COMMENT ON COLUMN source_normalization_rules.rule_type IS NULL")
    op.execute("COMMENT ON COLUMN source_normalization_rules.pattern IS NULL")
    op.execute("COMMENT ON COLUMN source_normalization_rules.replacement IS NULL")
    op.execute("COMMENT ON COLUMN source_normalization_rules.is_regex IS NULL")
    op.execute("COMMENT ON COLUMN source_normalization_rules.apply_to_sections IS NULL")
    op.execute("COMMENT ON COLUMN source_normalization_rules.priority IS NULL")
    op.execute("COMMENT ON COLUMN source_normalization_rules.is_active IS NULL")
    op.execute("COMMENT ON COLUMN source_normalization_rules.created_at IS NULL")
    op.execute("COMMENT ON COLUMN source_normalization_rules.updated_at IS NULL")

    # source_prompt_templates
    op.execute("COMMENT ON TABLE source_prompt_templates IS NULL")
    op.execute("COMMENT ON COLUMN source_prompt_templates.template_id IS NULL")
    op.execute("COMMENT ON COLUMN source_prompt_templates.source_id IS NULL")
    op.execute("COMMENT ON COLUMN source_prompt_templates.template_name IS NULL")
    op.execute("COMMENT ON COLUMN source_prompt_templates.template_type IS NULL")
    op.execute("COMMENT ON COLUMN source_prompt_templates.language_code IS NULL")
    op.execute("COMMENT ON COLUMN source_prompt_templates.prompt_text IS NULL")
    op.execute("COMMENT ON COLUMN source_prompt_templates.variables IS NULL")
    op.execute("COMMENT ON COLUMN source_prompt_templates.usage_count IS NULL")
    op.execute("COMMENT ON COLUMN source_prompt_templates.avg_confidence IS NULL")
    op.execute("COMMENT ON COLUMN source_prompt_templates.avg_tokens_used IS NULL")
    op.execute("COMMENT ON COLUMN source_prompt_templates.is_active IS NULL")
    op.execute("COMMENT ON COLUMN source_prompt_templates.version IS NULL")
    op.execute("COMMENT ON COLUMN source_prompt_templates.created_at IS NULL")
    op.execute("COMMENT ON COLUMN source_prompt_templates.updated_at IS NULL")

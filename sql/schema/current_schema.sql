-- Schema for dataminer database
-- Auto-generated from SQLAlchemy models
-- DO NOT EDIT MANUALLY - Use 'make schema-generate' to regenerate


CREATE TABLE IF NOT EXISTS document_sources (
	source_id VARCHAR(20) NOT NULL,
	source_name VARCHAR(200) NOT NULL,
	country_code VARCHAR(3),
	primary_language VARCHAR(10),
	secondary_languages VARCHAR(10)[],
	legal_system VARCHAR(50),
	document_type VARCHAR(100),
	is_active BOOLEAN DEFAULT true,
	phase INTEGER DEFAULT 1,
	total_documents_processed INTEGER DEFAULT 0,
	avg_accuracy NUMERIC(4, 2),
	avg_cost_per_document NUMERIC(10, 2),
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	CONSTRAINT pk_document_sources PRIMARY KEY (source_id)
)

;


CREATE TABLE IF NOT EXISTS source_extraction_profiles (
	profile_id UUID DEFAULT gen_random_uuid() NOT NULL,
	source_id VARCHAR(20) NOT NULL,
	profile_name VARCHAR(100) NOT NULL,
	is_active BOOLEAN DEFAULT true,
	is_default BOOLEAN DEFAULT false,
	pdf_extraction_method VARCHAR(50) DEFAULT 'pdfplumber',
	ocr_threshold NUMERIC(3, 2) DEFAULT 0.80,
	ocr_language VARCHAR(10),
	use_document_ai_fallback BOOLEAN DEFAULT true,
	segmentation_method VARCHAR(50) DEFAULT 'section_based',
	segment_size_tokens INTEGER DEFAULT 3000,
	segment_overlap_tokens INTEGER DEFAULT 200,
	llm_model_quick VARCHAR(50) DEFAULT 'gemini-1.5-flash',
	llm_model_detailed VARCHAR(50) DEFAULT 'gemini-1.5-pro',
	llm_temperature NUMERIC(2, 1) DEFAULT 0.1,
	max_retries INTEGER DEFAULT 2,
	max_cost_per_document NUMERIC(10, 2) DEFAULT 2.00,
	enable_deep_dive_pass BOOLEAN DEFAULT true,
	deep_dive_confidence_threshold NUMERIC(3, 2) DEFAULT 0.75,
	version INTEGER DEFAULT 1,
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	CONSTRAINT pk_source_extraction_profiles PRIMARY KEY (profile_id),
	CONSTRAINT fk_source_extraction_profiles_source_id_document_sources FOREIGN KEY(source_id) REFERENCES document_sources (source_id)
)

;


CREATE TABLE IF NOT EXISTS source_field_definitions (
	field_id UUID DEFAULT gen_random_uuid() NOT NULL,
	source_id VARCHAR(20) NOT NULL,
	field_name VARCHAR(100) NOT NULL,
	field_display_name VARCHAR(200),
	field_category VARCHAR(50),
	field_type VARCHAR(50),
	extraction_method VARCHAR(50),
	extraction_section VARCHAR(100),
	regex_pattern TEXT,
	llm_prompt_template_id UUID,
	is_required BOOLEAN DEFAULT false,
	validation_rules JSON,
	confidence_threshold NUMERIC(3, 2) DEFAULT 0.75,
	normalization_rules JSON,
	display_order INTEGER,
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	CONSTRAINT pk_source_field_definitions PRIMARY KEY (field_id),
	CONSTRAINT fk_source_field_definitions_source_id_document_sources FOREIGN KEY(source_id) REFERENCES document_sources (source_id)
)

;


CREATE TABLE IF NOT EXISTS source_normalization_rules (
	rule_id UUID DEFAULT gen_random_uuid() NOT NULL,
	source_id VARCHAR(20) NOT NULL,
	rule_name VARCHAR(100) NOT NULL,
	rule_type VARCHAR(50),
	pattern TEXT NOT NULL,
	replacement TEXT,
	is_regex BOOLEAN DEFAULT false,
	apply_to_sections VARCHAR(100)[],
	priority INTEGER DEFAULT 100,
	is_active BOOLEAN DEFAULT true,
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	CONSTRAINT pk_source_normalization_rules PRIMARY KEY (rule_id),
	CONSTRAINT fk_source_normalization_rules_source_id_document_sources FOREIGN KEY(source_id) REFERENCES document_sources (source_id)
)

;


CREATE TABLE IF NOT EXISTS source_prompt_templates (
	template_id UUID DEFAULT gen_random_uuid() NOT NULL,
	source_id VARCHAR(20) NOT NULL,
	template_name VARCHAR(100) NOT NULL,
	template_type VARCHAR(50),
	language_code VARCHAR(10),
	prompt_text TEXT NOT NULL,
	variables JSON,
	usage_count INTEGER DEFAULT 0,
	avg_confidence NUMERIC(3, 2),
	avg_tokens_used INTEGER,
	is_active BOOLEAN DEFAULT true,
	version INTEGER DEFAULT 1,
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	CONSTRAINT pk_source_prompt_templates PRIMARY KEY (template_id),
	CONSTRAINT fk_source_prompt_templates_source_id_document_sources FOREIGN KEY(source_id) REFERENCES document_sources (source_id)
)

;

-- Indexes

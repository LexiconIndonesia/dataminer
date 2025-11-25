-- Schema for dataminer database
-- Auto-generated from Alembic migrations
-- DO NOT EDIT MANUALLY - Use 'make schema-generate' to regenerate

--
-- PostgreSQL database dump
--



-- Dumped from database version 17.7 (Debian 17.7-3.pgdg12+1)
-- Dumped by pg_dump version 17.7 (Debian 17.7-3.pgdg12+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: document_sources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.document_sources (
    source_id character varying(20) NOT NULL,
    source_name character varying(200) NOT NULL,
    country_code character varying(3),
    primary_language character varying(10),
    secondary_languages character varying(10)[],
    legal_system character varying(50),
    document_type character varying(100),
    is_active boolean DEFAULT true,
    phase integer DEFAULT 1,
    total_documents_processed integer DEFAULT 0,
    avg_accuracy numeric(4,2),
    avg_cost_per_document numeric(10,2),
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


--
-- Name: TABLE document_sources; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.document_sources IS 'Master table for document sources (courts, agencies, etc.)';


--
-- Name: COLUMN document_sources.source_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_sources.source_id IS 'Unique identifier for the source (e.g., ID_SC for Indonesian Supreme Court)';


--
-- Name: COLUMN document_sources.source_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_sources.source_name IS 'Human-readable name of the document source';


--
-- Name: COLUMN document_sources.country_code; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_sources.country_code IS 'ISO 3166-1 alpha-3 country code (e.g., IDN, USA, GBR)';


--
-- Name: COLUMN document_sources.primary_language; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_sources.primary_language IS 'Primary language code (ISO 639-1, e.g., id, en)';


--
-- Name: COLUMN document_sources.secondary_languages; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_sources.secondary_languages IS 'Array of secondary language codes used in documents';


--
-- Name: COLUMN document_sources.legal_system; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_sources.legal_system IS 'Type of legal system (civil_law, common_law, mixed, religious)';


--
-- Name: COLUMN document_sources.document_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_sources.document_type IS 'Type of documents from this source (court_judgment, legislation, contract)';


--
-- Name: COLUMN document_sources.is_active; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_sources.is_active IS 'Whether this source is currently active for processing';


--
-- Name: COLUMN document_sources.phase; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_sources.phase IS 'Current processing phase (1=initial, 2=expanded, 3=full)';


--
-- Name: COLUMN document_sources.total_documents_processed; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_sources.total_documents_processed IS 'Running count of documents processed from this source';


--
-- Name: COLUMN document_sources.avg_accuracy; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_sources.avg_accuracy IS 'Average extraction accuracy score (0.00-1.00)';


--
-- Name: COLUMN document_sources.avg_cost_per_document; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_sources.avg_cost_per_document IS 'Average processing cost per document in USD';


--
-- Name: COLUMN document_sources.created_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_sources.created_at IS 'Timestamp when record was created';


--
-- Name: COLUMN document_sources.updated_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_sources.updated_at IS 'Timestamp when record was last updated';


--
-- Name: source_extraction_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.source_extraction_profiles (
    profile_id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_id character varying(20) NOT NULL,
    profile_name character varying(100) NOT NULL,
    is_active boolean DEFAULT true,
    is_default boolean DEFAULT false,
    pdf_extraction_method character varying(50) DEFAULT 'pdfplumber'::character varying,
    ocr_threshold numeric(3,2) DEFAULT 0.80,
    ocr_language character varying(10),
    use_document_ai_fallback boolean DEFAULT true,
    segmentation_method character varying(50) DEFAULT 'section_based'::character varying,
    segment_size_tokens integer DEFAULT 3000,
    segment_overlap_tokens integer DEFAULT 200,
    llm_model_quick character varying(50) DEFAULT 'gemini-1.5-flash'::character varying,
    llm_model_detailed character varying(50) DEFAULT 'gemini-1.5-pro'::character varying,
    llm_temperature numeric(2,1) DEFAULT 0.1,
    max_retries integer DEFAULT 2,
    max_cost_per_document numeric(10,2) DEFAULT 2.00,
    enable_deep_dive_pass boolean DEFAULT true,
    deep_dive_confidence_threshold numeric(3,2) DEFAULT 0.75,
    version integer DEFAULT 1,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


--
-- Name: TABLE source_extraction_profiles; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.source_extraction_profiles IS 'Extraction configuration profiles for each document source';


--
-- Name: COLUMN source_extraction_profiles.profile_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.profile_id IS 'Unique identifier for the profile (UUID)';


--
-- Name: COLUMN source_extraction_profiles.source_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.source_id IS 'Reference to the document source this profile belongs to';


--
-- Name: COLUMN source_extraction_profiles.profile_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.profile_name IS 'Human-readable name for this profile';


--
-- Name: COLUMN source_extraction_profiles.is_active; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.is_active IS 'Whether this profile is currently active';


--
-- Name: COLUMN source_extraction_profiles.is_default; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.is_default IS 'Whether this is the default profile for the source';


--
-- Name: COLUMN source_extraction_profiles.pdf_extraction_method; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.pdf_extraction_method IS 'PDF text extraction method (pdfplumber, pypdf2, pdfminer)';


--
-- Name: COLUMN source_extraction_profiles.ocr_threshold; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.ocr_threshold IS 'Text density threshold below which OCR is triggered (0.00-1.00)';


--
-- Name: COLUMN source_extraction_profiles.ocr_language; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.ocr_language IS 'Language code for OCR processing';


--
-- Name: COLUMN source_extraction_profiles.use_document_ai_fallback; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.use_document_ai_fallback IS 'Whether to use Document AI as fallback for failed extractions';


--
-- Name: COLUMN source_extraction_profiles.segmentation_method; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.segmentation_method IS 'Document segmentation method (section_based, fixed_size, semantic)';


--
-- Name: COLUMN source_extraction_profiles.segment_size_tokens; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.segment_size_tokens IS 'Target size of each segment in tokens';


--
-- Name: COLUMN source_extraction_profiles.segment_overlap_tokens; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.segment_overlap_tokens IS 'Number of overlapping tokens between segments';


--
-- Name: COLUMN source_extraction_profiles.llm_model_quick; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.llm_model_quick IS 'LLM model for quick/initial extraction passes';


--
-- Name: COLUMN source_extraction_profiles.llm_model_detailed; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.llm_model_detailed IS 'LLM model for detailed/deep extraction passes';


--
-- Name: COLUMN source_extraction_profiles.llm_temperature; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.llm_temperature IS 'Temperature setting for LLM inference (0.0-1.0)';


--
-- Name: COLUMN source_extraction_profiles.max_retries; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.max_retries IS 'Maximum retry attempts for failed extractions';


--
-- Name: COLUMN source_extraction_profiles.max_cost_per_document; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.max_cost_per_document IS 'Maximum allowed cost per document in USD';


--
-- Name: COLUMN source_extraction_profiles.enable_deep_dive_pass; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.enable_deep_dive_pass IS 'Whether to enable deep dive extraction pass for low-confidence fields';


--
-- Name: COLUMN source_extraction_profiles.deep_dive_confidence_threshold; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.deep_dive_confidence_threshold IS 'Confidence threshold below which deep dive is triggered (0.00-1.00)';


--
-- Name: COLUMN source_extraction_profiles.version; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.version IS 'Version number of this profile configuration';


--
-- Name: COLUMN source_extraction_profiles.created_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.created_at IS 'Timestamp when record was created';


--
-- Name: COLUMN source_extraction_profiles.updated_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_extraction_profiles.updated_at IS 'Timestamp when record was last updated';


--
-- Name: source_field_definitions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.source_field_definitions (
    field_id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_id character varying(20) NOT NULL,
    field_name character varying(100) NOT NULL,
    field_display_name character varying(200),
    field_category character varying(50),
    field_type character varying(50),
    extraction_method character varying(50),
    extraction_section character varying(100),
    regex_pattern text,
    llm_prompt_template_id uuid,
    is_required boolean DEFAULT false,
    validation_rules json,
    confidence_threshold numeric(3,2) DEFAULT 0.75,
    normalization_rules json,
    display_order integer,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


--
-- Name: TABLE source_field_definitions; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.source_field_definitions IS 'Field definitions for data extraction from each source';


--
-- Name: COLUMN source_field_definitions.field_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.field_id IS 'Unique identifier for the field (UUID)';


--
-- Name: COLUMN source_field_definitions.source_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.source_id IS 'Reference to the document source this field belongs to';


--
-- Name: COLUMN source_field_definitions.field_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.field_name IS 'Internal field name (snake_case, e.g., case_number)';


--
-- Name: COLUMN source_field_definitions.field_display_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.field_display_name IS 'Human-readable display name for the field';


--
-- Name: COLUMN source_field_definitions.field_category; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.field_category IS 'Category grouping (metadata, parties, decision, dates)';


--
-- Name: COLUMN source_field_definitions.field_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.field_type IS 'Data type (string, date, number, array, object)';


--
-- Name: COLUMN source_field_definitions.extraction_method; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.extraction_method IS 'How to extract this field (regex, llm, hybrid, rule_based)';


--
-- Name: COLUMN source_field_definitions.extraction_section; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.extraction_section IS 'Document section to search for this field';


--
-- Name: COLUMN source_field_definitions.regex_pattern; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.regex_pattern IS 'Regular expression pattern for regex extraction';


--
-- Name: COLUMN source_field_definitions.llm_prompt_template_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.llm_prompt_template_id IS 'Reference to prompt template for LLM extraction';


--
-- Name: COLUMN source_field_definitions.is_required; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.is_required IS 'Whether this field is required for valid extraction';


--
-- Name: COLUMN source_field_definitions.validation_rules; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.validation_rules IS 'JSON object with validation rules for the field';


--
-- Name: COLUMN source_field_definitions.confidence_threshold; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.confidence_threshold IS 'Minimum confidence score to accept extraction (0.00-1.00)';


--
-- Name: COLUMN source_field_definitions.normalization_rules; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.normalization_rules IS 'JSON object with normalization/transformation rules';


--
-- Name: COLUMN source_field_definitions.display_order; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.display_order IS 'Order in which to display this field in UI';


--
-- Name: COLUMN source_field_definitions.created_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.created_at IS 'Timestamp when record was created';


--
-- Name: COLUMN source_field_definitions.updated_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_field_definitions.updated_at IS 'Timestamp when record was last updated';


--
-- Name: source_normalization_rules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.source_normalization_rules (
    rule_id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_id character varying(20) NOT NULL,
    rule_name character varying(100) NOT NULL,
    rule_type character varying(50),
    pattern text NOT NULL,
    replacement text,
    is_regex boolean DEFAULT false,
    apply_to_sections character varying(100)[],
    priority integer DEFAULT 100,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


--
-- Name: TABLE source_normalization_rules; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.source_normalization_rules IS 'Text normalization rules for cleaning extracted content';


--
-- Name: COLUMN source_normalization_rules.rule_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_normalization_rules.rule_id IS 'Unique identifier for the rule (UUID)';


--
-- Name: COLUMN source_normalization_rules.source_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_normalization_rules.source_id IS 'Reference to the document source this rule belongs to';


--
-- Name: COLUMN source_normalization_rules.rule_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_normalization_rules.rule_name IS 'Human-readable name for this rule';


--
-- Name: COLUMN source_normalization_rules.rule_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_normalization_rules.rule_type IS 'Type of normalization (whitespace, unicode, case, custom)';


--
-- Name: COLUMN source_normalization_rules.pattern; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_normalization_rules.pattern IS 'Pattern to match (string or regex based on is_regex)';


--
-- Name: COLUMN source_normalization_rules.replacement; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_normalization_rules.replacement IS 'Replacement text for matched pattern';


--
-- Name: COLUMN source_normalization_rules.is_regex; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_normalization_rules.is_regex IS 'Whether pattern is a regular expression';


--
-- Name: COLUMN source_normalization_rules.apply_to_sections; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_normalization_rules.apply_to_sections IS 'Array of section names where this rule applies';


--
-- Name: COLUMN source_normalization_rules.priority; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_normalization_rules.priority IS 'Execution priority (lower numbers run first)';


--
-- Name: COLUMN source_normalization_rules.is_active; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_normalization_rules.is_active IS 'Whether this rule is currently active';


--
-- Name: COLUMN source_normalization_rules.created_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_normalization_rules.created_at IS 'Timestamp when record was created';


--
-- Name: COLUMN source_normalization_rules.updated_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_normalization_rules.updated_at IS 'Timestamp when record was last updated';


--
-- Name: source_prompt_templates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.source_prompt_templates (
    template_id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_id character varying(20) NOT NULL,
    template_name character varying(100) NOT NULL,
    template_type character varying(50),
    language_code character varying(10),
    prompt_text text NOT NULL,
    variables json,
    usage_count integer DEFAULT 0,
    avg_confidence numeric(3,2),
    avg_tokens_used integer,
    is_active boolean DEFAULT true,
    version integer DEFAULT 1,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


--
-- Name: TABLE source_prompt_templates; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.source_prompt_templates IS 'LLM prompt templates for field extraction';


--
-- Name: COLUMN source_prompt_templates.template_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_prompt_templates.template_id IS 'Unique identifier for the template (UUID)';


--
-- Name: COLUMN source_prompt_templates.source_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_prompt_templates.source_id IS 'Reference to the document source this template belongs to';


--
-- Name: COLUMN source_prompt_templates.template_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_prompt_templates.template_name IS 'Human-readable name for this template';


--
-- Name: COLUMN source_prompt_templates.template_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_prompt_templates.template_type IS 'Type of prompt (extraction, validation, summarization)';


--
-- Name: COLUMN source_prompt_templates.language_code; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_prompt_templates.language_code IS 'Language code for this template (for multi-language support)';


--
-- Name: COLUMN source_prompt_templates.prompt_text; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_prompt_templates.prompt_text IS 'The actual prompt template text';


--
-- Name: COLUMN source_prompt_templates.variables; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_prompt_templates.variables IS 'JSON array of variable names used in the template';


--
-- Name: COLUMN source_prompt_templates.usage_count; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_prompt_templates.usage_count IS 'Number of times this template has been used';


--
-- Name: COLUMN source_prompt_templates.avg_confidence; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_prompt_templates.avg_confidence IS 'Average confidence score from extractions using this template';


--
-- Name: COLUMN source_prompt_templates.avg_tokens_used; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_prompt_templates.avg_tokens_used IS 'Average tokens consumed per use';


--
-- Name: COLUMN source_prompt_templates.is_active; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_prompt_templates.is_active IS 'Whether this template is currently active';


--
-- Name: COLUMN source_prompt_templates.version; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_prompt_templates.version IS 'Version number of this template';


--
-- Name: COLUMN source_prompt_templates.created_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_prompt_templates.created_at IS 'Timestamp when record was created';


--
-- Name: COLUMN source_prompt_templates.updated_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.source_prompt_templates.updated_at IS 'Timestamp when record was last updated';


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: document_sources document_sources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_sources
    ADD CONSTRAINT document_sources_pkey PRIMARY KEY (source_id);


--
-- Name: source_extraction_profiles source_extraction_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source_extraction_profiles
    ADD CONSTRAINT source_extraction_profiles_pkey PRIMARY KEY (profile_id);


--
-- Name: source_field_definitions source_field_definitions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source_field_definitions
    ADD CONSTRAINT source_field_definitions_pkey PRIMARY KEY (field_id);


--
-- Name: source_normalization_rules source_normalization_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source_normalization_rules
    ADD CONSTRAINT source_normalization_rules_pkey PRIMARY KEY (rule_id);


--
-- Name: source_prompt_templates source_prompt_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source_prompt_templates
    ADD CONSTRAINT source_prompt_templates_pkey PRIMARY KEY (template_id);


--
-- Name: source_extraction_profiles source_extraction_profiles_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source_extraction_profiles
    ADD CONSTRAINT source_extraction_profiles_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.document_sources(source_id);


--
-- Name: source_field_definitions source_field_definitions_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source_field_definitions
    ADD CONSTRAINT source_field_definitions_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.document_sources(source_id);


--
-- Name: source_normalization_rules source_normalization_rules_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source_normalization_rules
    ADD CONSTRAINT source_normalization_rules_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.document_sources(source_id);


--
-- Name: source_prompt_templates source_prompt_templates_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source_prompt_templates
    ADD CONSTRAINT source_prompt_templates_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.document_sources(source_id);


--
-- PostgreSQL database dump complete
--

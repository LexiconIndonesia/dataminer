"""Configuration database models."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import (
    ARRAY,
    JSON,
    TIMESTAMP,
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dataminer.db.base import Base


class DocumentSource(Base):
    """Document source configuration table."""

    __tablename__ = "document_sources"

    source_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    source_name: Mapped[str] = mapped_column(String(200), nullable=False)
    country_code: Mapped[str | None] = mapped_column(String(3))
    primary_language: Mapped[str | None] = mapped_column(String(10))
    secondary_languages: Mapped[list[str] | None] = mapped_column(ARRAY(String(10)))
    legal_system: Mapped[str | None] = mapped_column(String(50))
    document_type: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("true"))
    phase: Mapped[int | None] = mapped_column(Integer, server_default=text("1"))
    total_documents_processed: Mapped[int | None] = mapped_column(Integer, server_default=text("0"))
    avg_accuracy: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    avg_cost_per_document: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, server_default=text("NOW()"))
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, server_default=text("NOW()"))

    # Relationships
    extraction_profiles: Mapped[list[SourceExtractionProfile]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )
    field_definitions: Mapped[list[SourceFieldDefinition]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )
    normalization_rules: Mapped[list[SourceNormalizationRule]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )
    prompt_templates: Mapped[list[SourcePromptTemplate]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )


class SourceExtractionProfile(Base):
    """Source extraction profile configuration table."""

    __tablename__ = "source_extraction_profiles"

    profile_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    source_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("document_sources.source_id"), nullable=False
    )
    profile_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("true"))
    is_default: Mapped[bool | None] = mapped_column(Boolean, server_default=text("false"))
    pdf_extraction_method: Mapped[str | None] = mapped_column(
        String(50), server_default=text("'pdfplumber'")
    )
    ocr_threshold: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2), server_default=text("0.80")
    )
    ocr_language: Mapped[str | None] = mapped_column(String(10))
    use_document_ai_fallback: Mapped[bool | None] = mapped_column(
        Boolean, server_default=text("true")
    )
    segmentation_method: Mapped[str | None] = mapped_column(
        String(50), server_default=text("'section_based'")
    )
    segment_size_tokens: Mapped[int | None] = mapped_column(Integer, server_default=text("3000"))
    segment_overlap_tokens: Mapped[int | None] = mapped_column(Integer, server_default=text("200"))
    llm_model_quick: Mapped[str | None] = mapped_column(
        String(50), server_default=text("'gemini-1.5-flash'")
    )
    llm_model_detailed: Mapped[str | None] = mapped_column(
        String(50), server_default=text("'gemini-1.5-pro'")
    )
    llm_temperature: Mapped[Decimal | None] = mapped_column(
        Numeric(2, 1), server_default=text("0.1")
    )
    max_retries: Mapped[int | None] = mapped_column(Integer, server_default=text("2"))
    max_cost_per_document: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), server_default=text("2.00")
    )
    enable_deep_dive_pass: Mapped[bool | None] = mapped_column(Boolean, server_default=text("true"))
    deep_dive_confidence_threshold: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2), server_default=text("0.75")
    )
    version: Mapped[int | None] = mapped_column(Integer, server_default=text("1"))
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, server_default=text("NOW()"))
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, server_default=text("NOW()"))

    # Relationship
    source: Mapped[DocumentSource] = relationship(back_populates="extraction_profiles")


class SourceFieldDefinition(Base):
    """Source field definition table."""

    __tablename__ = "source_field_definitions"

    field_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    source_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("document_sources.source_id"), nullable=False
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    field_display_name: Mapped[str | None] = mapped_column(String(200))
    field_category: Mapped[str | None] = mapped_column(String(50))
    field_type: Mapped[str | None] = mapped_column(String(50))
    extraction_method: Mapped[str | None] = mapped_column(String(50))
    extraction_section: Mapped[str | None] = mapped_column(String(100))
    regex_pattern: Mapped[str | None] = mapped_column(Text)
    llm_prompt_template_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True))
    is_required: Mapped[bool | None] = mapped_column(Boolean, server_default=text("false"))
    validation_rules: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    confidence_threshold: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2), server_default=text("0.75")
    )
    normalization_rules: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    display_order: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, server_default=text("NOW()"))
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, server_default=text("NOW()"))

    # Relationship
    source: Mapped[DocumentSource] = relationship(back_populates="field_definitions")


class SourceNormalizationRule(Base):
    """Source normalization rule table."""

    __tablename__ = "source_normalization_rules"

    rule_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    source_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("document_sources.source_id"), nullable=False
    )
    rule_name: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_type: Mapped[str | None] = mapped_column(String(50))
    pattern: Mapped[str] = mapped_column(Text, nullable=False)
    replacement: Mapped[str | None] = mapped_column(Text)
    is_regex: Mapped[bool | None] = mapped_column(Boolean, server_default=text("false"))
    apply_to_sections: Mapped[list[str] | None] = mapped_column(ARRAY(String(100)))
    priority: Mapped[int | None] = mapped_column(Integer, server_default=text("100"))
    is_active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("true"))
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, server_default=text("NOW()"))
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, server_default=text("NOW()"))

    # Relationship
    source: Mapped[DocumentSource] = relationship(back_populates="normalization_rules")


class SourcePromptTemplate(Base):
    """Source prompt template table."""

    __tablename__ = "source_prompt_templates"

    template_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    source_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("document_sources.source_id"), nullable=False
    )
    template_name: Mapped[str] = mapped_column(String(100), nullable=False)
    template_type: Mapped[str | None] = mapped_column(String(50))
    language_code: Mapped[str | None] = mapped_column(String(10))
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    usage_count: Mapped[int | None] = mapped_column(Integer, server_default=text("0"))
    avg_confidence: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))
    avg_tokens_used: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("true"))
    version: Mapped[int | None] = mapped_column(Integer, server_default=text("1"))
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, server_default=text("NOW()"))
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, server_default=text("NOW()"))

    # Relationship
    source: Mapped[DocumentSource] = relationship(back_populates="prompt_templates")

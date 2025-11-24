"""Source management API schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# Document Source Schemas
class DocumentSourceBase(BaseModel):
    """Base document source schema."""

    source_name: str = Field(..., max_length=200, description="Source display name")
    country_code: str | None = Field(None, max_length=3, description="ISO country code")
    primary_language: str | None = Field(None, max_length=10, description="Primary language code")
    secondary_languages: list[str] | None = Field(
        None, description="List of secondary language codes"
    )
    legal_system: str | None = Field(None, max_length=50, description="Legal system type")
    document_type: str | None = Field(None, max_length=100, description="Type of documents")
    is_active: bool | None = Field(True, description="Whether source is active")
    phase: int | None = Field(1, ge=1, le=5, description="Development phase number (1-5)")

    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, v: str | None) -> str | None:
        """Validate country code is uppercase."""
        if v is not None:
            return v.upper()
        return v

    @field_validator("secondary_languages")
    @classmethod
    def validate_language_codes(cls, v: list[str] | None) -> list[str] | None:
        """Validate language codes are lowercase."""
        if v is not None:
            return [lang.lower() for lang in v]
        return v


class DocumentSourceCreate(DocumentSourceBase):
    """Schema for creating a new document source."""

    source_id: str = Field(..., max_length=20, description="Unique source identifier")


class DocumentSourceUpdate(BaseModel):
    """Schema for updating document source configuration."""

    source_name: str | None = Field(None, max_length=200)
    is_active: bool | None = None
    phase: int | None = None
    avg_accuracy: Decimal | None = Field(None, ge=0, le=1, decimal_places=2)
    avg_cost_per_document: Decimal | None = Field(None, ge=0, decimal_places=2)


class DocumentSourceResponse(DocumentSourceBase):
    """Schema for document source response."""

    model_config = ConfigDict(from_attributes=True)

    source_id: str
    total_documents_processed: int | None = None
    avg_accuracy: Decimal | None = None
    avg_cost_per_document: Decimal | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


# Extraction Profile Schemas
class ExtractionProfileBase(BaseModel):
    """Base extraction profile schema."""

    profile_name: str = Field(..., max_length=100, description="Profile display name")
    is_active: bool | None = Field(True, description="Whether profile is active")
    is_default: bool | None = Field(False, description="Whether this is the default profile")
    pdf_extraction_method: str | None = Field(
        "pdfplumber", max_length=50, description="PDF extraction method"
    )
    ocr_threshold: Decimal | None = Field(
        Decimal("0.80"), ge=0, le=1, decimal_places=2, description="OCR quality threshold"
    )
    ocr_language: str | None = Field(None, max_length=10, description="OCR language code")
    use_document_ai_fallback: bool | None = Field(True, description="Use Document AI as fallback")
    segmentation_method: str | None = Field(
        "section_based", max_length=50, description="Text segmentation method"
    )
    segment_size_tokens: int | None = Field(
        3000, ge=100, le=10000, description="Segment size in tokens"
    )
    segment_overlap_tokens: int | None = Field(
        200, ge=0, le=1000, description="Segment overlap in tokens"
    )
    llm_model_quick: str | None = Field(
        "gemini-1.5-flash", max_length=50, description="Quick LLM model"
    )
    llm_model_detailed: str | None = Field(
        "gemini-1.5-pro", max_length=50, description="Detailed LLM model"
    )
    llm_temperature: Decimal | None = Field(
        Decimal("0.1"), ge=0, le=2, decimal_places=1, description="LLM temperature"
    )
    max_retries: int | None = Field(2, ge=0, le=10, description="Maximum retry attempts")
    max_cost_per_document: Decimal | None = Field(
        Decimal("2.00"), ge=0, decimal_places=2, description="Maximum cost per document"
    )
    enable_deep_dive_pass: bool | None = Field(True, description="Enable deep dive pass")
    deep_dive_confidence_threshold: Decimal | None = Field(
        Decimal("0.75"), ge=0, le=1, decimal_places=2, description="Deep dive confidence threshold"
    )

    @model_validator(mode="after")
    def validate_segment_tokens(self) -> ExtractionProfileBase:
        """Validate segment token configuration."""
        if (
            self.segment_overlap_tokens is not None
            and self.segment_size_tokens is not None
            and self.segment_overlap_tokens >= self.segment_size_tokens
        ):
            raise ValueError(
                f"segment_overlap_tokens ({self.segment_overlap_tokens}) must be less than "
                f"segment_size_tokens ({self.segment_size_tokens})"
            )
        return self


class ExtractionProfileCreate(ExtractionProfileBase):
    """Schema for creating a new extraction profile."""

    pass


class ExtractionProfileUpdate(BaseModel):
    """Schema for updating an extraction profile."""

    profile_name: str | None = Field(None, max_length=100)
    is_active: bool | None = None
    is_default: bool | None = None
    pdf_extraction_method: str | None = None
    ocr_threshold: Decimal | None = Field(None, ge=0, le=1, decimal_places=2)
    llm_model_quick: str | None = None
    llm_model_detailed: str | None = None
    llm_temperature: Decimal | None = Field(None, ge=0, le=2, decimal_places=1)
    max_cost_per_document: Decimal | None = Field(None, ge=0, decimal_places=2)


class ExtractionProfileResponse(ExtractionProfileBase):
    """Schema for extraction profile response."""

    model_config = ConfigDict(from_attributes=True)

    profile_id: UUID
    source_id: str | None = None
    version: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

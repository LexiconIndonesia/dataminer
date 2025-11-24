-- name: ListProfilesBySource :many
SELECT profile_id, source_id, profile_name, is_active, is_default,
       pdf_extraction_method, ocr_threshold, ocr_language, use_document_ai_fallback,
       segmentation_method, segment_size_tokens, segment_overlap_tokens,
       llm_model_quick, llm_model_detailed, llm_temperature, max_retries,
       max_cost_per_document, enable_deep_dive_pass, deep_dive_confidence_threshold,
       version, created_at, updated_at
FROM source_extraction_profiles
WHERE source_id = $1
ORDER BY created_at;

-- name: GetProfileByID :one
SELECT profile_id, source_id, profile_name, is_active, is_default,
       pdf_extraction_method, ocr_threshold, ocr_language, use_document_ai_fallback,
       segmentation_method, segment_size_tokens, segment_overlap_tokens,
       llm_model_quick, llm_model_detailed, llm_temperature, max_retries,
       max_cost_per_document, enable_deep_dive_pass, deep_dive_confidence_threshold,
       version, created_at, updated_at
FROM source_extraction_profiles
WHERE profile_id = $1;

-- name: CreateProfile :one
INSERT INTO source_extraction_profiles (
    source_id, profile_name, is_active, is_default, pdf_extraction_method,
    ocr_threshold, ocr_language, use_document_ai_fallback, segmentation_method,
    segment_size_tokens, segment_overlap_tokens, llm_model_quick, llm_model_detailed,
    llm_temperature, max_retries, max_cost_per_document, enable_deep_dive_pass,
    deep_dive_confidence_threshold
) VALUES (
    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18
)
RETURNING profile_id, source_id, profile_name, is_active, is_default,
          pdf_extraction_method, ocr_threshold, ocr_language, use_document_ai_fallback,
          segmentation_method, segment_size_tokens, segment_overlap_tokens,
          llm_model_quick, llm_model_detailed, llm_temperature, max_retries,
          max_cost_per_document, enable_deep_dive_pass, deep_dive_confidence_threshold,
          version, created_at, updated_at;

-- name: CheckDuplicateProfileName :one
SELECT EXISTS(
    SELECT 1 FROM source_extraction_profiles
    WHERE source_id = $1 AND profile_name = $2
) AS exists;

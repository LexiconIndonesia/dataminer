-- name: ListFieldsBySource :many
SELECT field_id, source_id, field_name, field_display_name, field_category,
       field_type, extraction_method, extraction_section, regex_pattern,
       llm_prompt_template_id, is_required, validation_rules, confidence_threshold,
       normalization_rules, display_order, created_at, updated_at
FROM source_field_definitions
WHERE source_id = $1
ORDER BY COALESCE(display_order, 9999), field_name;

-- name: ListFieldsBySourceFiltered :many
SELECT field_id, source_id, field_name, field_display_name, field_category,
       field_type, extraction_method, extraction_section, regex_pattern,
       llm_prompt_template_id, is_required, validation_rules, confidence_threshold,
       normalization_rules, display_order, created_at, updated_at
FROM source_field_definitions
WHERE source_id = sqlc.arg('source_id')
  AND (sqlc.narg('field_category')::VARCHAR IS NULL OR field_category = sqlc.narg('field_category'))
  AND (sqlc.narg('field_type')::VARCHAR IS NULL OR field_type = sqlc.narg('field_type'))
  AND (sqlc.narg('is_required')::BOOLEAN IS NULL OR is_required = sqlc.narg('is_required'))
ORDER BY COALESCE(display_order, 9999), field_name
LIMIT sqlc.arg('limit_val')
OFFSET sqlc.arg('offset_val');

-- name: CountFieldsBySourceFiltered :one
SELECT COUNT(*) AS total
FROM source_field_definitions
WHERE source_id = sqlc.arg('source_id')
  AND (sqlc.narg('field_category')::VARCHAR IS NULL OR field_category = sqlc.narg('field_category'))
  AND (sqlc.narg('field_type')::VARCHAR IS NULL OR field_type = sqlc.narg('field_type'))
  AND (sqlc.narg('is_required')::BOOLEAN IS NULL OR is_required = sqlc.narg('is_required'));

-- name: GetFieldByID :one
SELECT field_id, source_id, field_name, field_display_name, field_category,
       field_type, extraction_method, extraction_section, regex_pattern,
       llm_prompt_template_id, is_required, validation_rules, confidence_threshold,
       normalization_rules, display_order, created_at, updated_at
FROM source_field_definitions
WHERE field_id = $1;

-- name: CreateField :one
INSERT INTO source_field_definitions (
    source_id, field_name, field_display_name, field_category, field_type,
    extraction_method, extraction_section, regex_pattern, llm_prompt_template_id,
    is_required, validation_rules, confidence_threshold, normalization_rules,
    display_order
) VALUES (
    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14
)
RETURNING field_id, source_id, field_name, field_display_name, field_category,
          field_type, extraction_method, extraction_section, regex_pattern,
          llm_prompt_template_id, is_required, validation_rules, confidence_threshold,
          normalization_rules, display_order, created_at, updated_at;

-- name: UpdateField :one
UPDATE source_field_definitions
SET field_name = COALESCE(sqlc.narg('field_name'), field_name),
    field_display_name = COALESCE(sqlc.narg('field_display_name'), field_display_name),
    field_category = COALESCE(sqlc.narg('field_category'), field_category),
    field_type = COALESCE(sqlc.narg('field_type'), field_type),
    extraction_method = COALESCE(sqlc.narg('extraction_method'), extraction_method),
    extraction_section = COALESCE(sqlc.narg('extraction_section'), extraction_section),
    regex_pattern = COALESCE(sqlc.narg('regex_pattern'), regex_pattern),
    llm_prompt_template_id = COALESCE(sqlc.narg('llm_prompt_template_id'), llm_prompt_template_id),
    is_required = COALESCE(sqlc.narg('is_required'), is_required),
    validation_rules = COALESCE(sqlc.narg('validation_rules'), validation_rules),
    confidence_threshold = COALESCE(sqlc.narg('confidence_threshold'), confidence_threshold),
    normalization_rules = COALESCE(sqlc.narg('normalization_rules'), normalization_rules),
    display_order = COALESCE(sqlc.narg('display_order'), display_order),
    updated_at = NOW()
WHERE field_id = sqlc.arg('field_id')
RETURNING field_id, source_id, field_name, field_display_name, field_category,
          field_type, extraction_method, extraction_section, regex_pattern,
          llm_prompt_template_id, is_required, validation_rules, confidence_threshold,
          normalization_rules, display_order, created_at, updated_at;

-- name: DeleteField :exec
DELETE FROM source_field_definitions
WHERE field_id = $1;

-- name: CheckDuplicateFieldName :one
SELECT EXISTS(
    SELECT 1 FROM source_field_definitions
    WHERE source_id = $1 AND field_name = $2
) AS exists;

-- name: CheckDuplicateFieldNameExcluding :one
SELECT EXISTS(
    SELECT 1 FROM source_field_definitions
    WHERE source_id = $1 AND field_name = $2 AND field_id != $3
) AS exists;

-- name: GetFieldSourceID :one
SELECT source_id FROM source_field_definitions
WHERE field_id = $1;

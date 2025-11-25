-- name: ListSources :many
SELECT source_id, source_name, country_code, primary_language, secondary_languages,
       legal_system, document_type, is_active, phase, total_documents_processed,
       avg_accuracy, avg_cost_per_document, created_at, updated_at
FROM document_sources
ORDER BY source_id;

-- name: GetSourceByID :one
SELECT source_id, source_name, country_code, primary_language, secondary_languages,
       legal_system, document_type, is_active, phase, total_documents_processed,
       avg_accuracy, avg_cost_per_document, created_at, updated_at
FROM document_sources
WHERE source_id = $1;

-- name: CreateSource :one
INSERT INTO document_sources (
    source_id, source_name, country_code, primary_language, secondary_languages,
    legal_system, document_type, is_active, phase
) VALUES (
    $1, $2, $3, $4, $5, $6, $7, $8, $9
)
RETURNING source_id, source_name, country_code, primary_language, secondary_languages,
          legal_system, document_type, is_active, phase, total_documents_processed,
          avg_accuracy, avg_cost_per_document, created_at, updated_at;

-- name: UpdateSource :one
UPDATE document_sources
SET source_name = COALESCE(sqlc.narg('source_name'), source_name),
    is_active = COALESCE(sqlc.narg('is_active'), is_active),
    phase = COALESCE(sqlc.narg('phase'), phase),
    avg_accuracy = COALESCE(sqlc.narg('avg_accuracy'), avg_accuracy),
    avg_cost_per_document = COALESCE(sqlc.narg('avg_cost_per_document'), avg_cost_per_document),
    updated_at = NOW()
WHERE source_id = sqlc.arg('source_id')
RETURNING source_id, source_name, country_code, primary_language, secondary_languages,
          legal_system, document_type, is_active, phase, total_documents_processed,
          avg_accuracy, avg_cost_per_document, created_at, updated_at;

"""Persist candidate retrieval across commands without relying on worker memory."""
import hashlib
import json

from django.db import connection


def snapshot_key(options):
    return hashlib.sha256(json.dumps(options, sort_keys=True).encode()).hexdigest()


def read_snapshot(key):
    # Order-independent content checksums detect bulk SQL loads and same-count
    # replacements, neither of which emits Django signals. Numeric sums avoid
    # bigint overflow. Counts distinguish empty tables and duplicate rows.
    # This is one query, but scans the inputs; it avoids per-code trigram work.
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH inputs AS (
                SELECT 'concept' AS kind, count(*) AS n,
                       coalesce(sum(hashtextextended(
                           ROW(concept_id, concept_name, domain_id,
                               standard_concept, invalid_reason)::text, 0)::numeric), 0) AS digest
                FROM concept
                UNION ALL
                SELECT 'synonym', count(*),
                       coalesce(sum(hashtextextended(
                           ROW(concept_id, concept_synonym_name)::text, 0)::numeric), 0)
                FROM concept_synonym
                UNION ALL
                SELECT 'queue', count(*),
                       coalesce(sum(hashtextextended(
                           ROW(id, source_vocabulary_id, source_code,
                               source_code_description, umls_source_name,
                               source_concept_id, domain_id, omop_table,
                               occurrence_count)::text, 0)::numeric), 0)
                FROM source_code_concept_mapping
                WHERE status = 'proposed'
                  AND (origin_system = '' OR origin_system ILIKE 'suggest%%')
            ), fingerprint AS (
                SELECT jsonb_agg(jsonb_build_array(kind, n, digest::text)
                                 ORDER BY kind) AS value
                FROM inputs
            )
            SELECT fingerprint.value, snapshot.fingerprint,
                   snapshot.candidate_ids,
                   EXISTS (
                       SELECT 1
                       FROM jsonb_array_elements_text(snapshot.candidate_ids) AS candidate(id)
                       WHERE NOT EXISTS (
                           SELECT 1 FROM concept_embedding
                           WHERE concept_id = candidate.id::bigint
                       )
                   ) AS missing
            FROM fingerprint
            LEFT JOIN suggest_embedding_snapshot AS snapshot ON snapshot.key = %s
        """, [key])
        current, cached, candidate_ids, missing = cursor.fetchone()

    # Django's PostgreSQL connection returns raw JSON strings for JSONField
    # decoding; raw cursors do not apply the model field's decoder.
    current = json.loads(current) if isinstance(current, str) else current
    cached = json.loads(cached) if isinstance(cached, str) else cached
    candidate_ids = json.loads(candidate_ids) if isinstance(candidate_ids, str) else candidate_ids
    return current, candidate_ids if current == cached else None, missing

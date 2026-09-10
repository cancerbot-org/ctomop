# Semantic retrieval for code-mapping suggestions

The Code Mapping toolbar and single-code dialog offer **UMLS**, **Lexical**,
**Semantic retrieval**, enabled by default. The API strategy names are `umls`,
`lexical`, and `semantic` respectively.
Explicit strategy lists continue to run only the requested strategies.

A single UMLS match still bypasses other retrieval and the LLM. Otherwise,
every enabled retriever contributes candidates: semantic retrieval runs even
when lexical search finds matches. It retrieves up to ten nearest embedded
concepts by cosine distance, restricted to active standard concepts and the
applicable domain. ICD-10 sources retain their cross-domain search behavior.
The pool is deduplicated by concept ID; duplicates retain UMLS/lexical
provenance and gain a `semantic_score` (cosine similarity, not confidence).

There is no vector-reranking step in the default pipeline: the entire pool goes
to one existing LLM selection call, which can abstain. Fallback precedence is
UMLS, lexical, then semantic, with each tier retaining its own retrieval order.
Older API clients may still explicitly request `vectors` to rerank UMLS and
lexical candidates within their tiers. Semantic candidates are never reranked
with the same model; they already have cosine order.
Suggestions remain proposed until reviewed. Semantic selections are recorded
with `suggest_strategy=semantic`; suggestion algorithm version is `v0.4`.

## Setup

No additional service or LLM is required. Install PROMOP's existing
`sentence-transformers` dependency and use PostgreSQL with pgvector.
`concept_embedding` must contain BAAI/bge-small-en-v1.5 embeddings (384
dimensions) of concept names, generated with the same model as query encoding.

Build embeddings for the vocabulary coverage you intend to search:

```sh
python manage.py build_concept_embeddings
# Or limit coverage, for example:
python manage.py build_concept_embeddings --vocabulary-id LOINC
```

The command also builds the existing IVFFlat cosine index. The shortlist-only
`precompute_suggest_embeddings` command remains useful for reranking but cannot
provide full semantic retrieval coverage: unembedded concepts cannot be found.
Re-run the full builder after vocabulary updates; use `--force` to regenerate
embeddings when concept names change. Check query plans and recall on a
representative database before making performance or accuracy claims.

`SUGGEST_SEMANTIC_TIMEOUT_MS` bounds each nearest-neighbour database query
(default 3000 ms). Model loading and query encoding are outside this timeout.
A missing model, unavailable embeddings, or a failed/timed-out semantic query
contributes no semantic candidates; other retrieval continues. Failures are
logged. The timeout is scoped and restored so later queries are unaffected.

## Attribution

This strategy adapts [Lettuce](https://github.com/Health-Informatics-UoN/lettuce)'s
filtered cosine retrieval approach. See [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)
and its [MIT license notice](../licenses/lettuce-MIT.txt).

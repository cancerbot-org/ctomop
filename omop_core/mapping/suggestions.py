"""Suggest destination concepts for source codes nobody has mapped yet.

The Code Mapping queue is only useful if something fills it. Ingest fills it for
codes it meets: every unresolved code gets a ``proposed`` row through
``_record_proposal``, so the tab *is* the queue. Suggest's job is to put a
destination on the rows sitting there without one.

**Suggest reads the tab, not the clinical tables.** It used to re-derive the
queue on every run by grouping the whole clinical table on ``concept_id = 0``
and subtracting every row already in ``source_code_concept_mapping``. That cost
4-7s per table before a single candidate was retrieved, and by the time ingest
was creating a queue row for every code it met, it returned *nothing* on the
tabs that actually have a backlog -- measured on staging, 0 codes for both
ICD10 (10,334 rows awaiting review) and RxNorm (3,856). Suggest scanned for
minutes and proposed nothing. ``enqueue_unmapped_source_codes`` still does that
scan, as the batch job it always was; see its docstring.

**Only rows nobody has spoken for.** A row is eligible when its provenance
(``origin_system``) is empty or begins with ``suggest`` -- that is, when the
only thing that ever set it was a previous Suggest run. An ``HT-One`` or
``HT-FHIR`` row carries a destination its importer asserted, and re-deriving
that from the source text would overwrite a better answer with a worse one.
``approved`` and ``rejected`` are decisions and are never touched.

Retrieval then ranking, and the order within retrieval is the point:

**1. UMLS.** CUI bridging is a curated NLM equivalency, so a single standard
concept ends the pipeline with no model call at all.

**2. Lexical, for the candidate subset.** The GIN trigram indexes narrow via the
``%`` operator; ``similarity()`` then scores only the survivors. Scoring first
seq-scans 2.4M synonym rows -- 4.49s for one source value. A synonym hit is
worth more than a name hit -- synonyms are the terms clinicians actually write,
which is what a source value is. How many survive is the caller's choice
(``lexical_limit``), because it is the one knob that trades recall against the
size of everything downstream.

**3. Vectors, to rank that subset.** Embedding similarity is a far better
*ordering* than trigram overlap and a far worse *filter*: as a retrieval tier it
cosine-scanned 1.5M stored vectors per source code, 2.6-2.9s each on staging,
to produce a rival shortlist that then needed its own ranker call. Reranking the
shortlist costs one query embedding and a primary-key lookup of at most
``lexical_limit`` stored vectors.

**4. One ranking call.** For ``SERUM FREE LIGHT CHAIN KAPPA`` trigram's top hit
is *Free kappa/lambda light chain ratio in serum* (0.67) -- a ratio, clinically
the wrong quantity -- while the correct *Kappa light chains.free [Mass/volume]
in Serum* sits third at 0.64. Retrieval put the answer in the shortlist and
ranking buried it. So a model re-ranks the shortlist -- **once**. The previous
waterfall gave each tier its own ranker call and took the first tier that
answered, so a code that fell through UMLS and vectors paid for three model
calls at 4-6s each and was usually given the lexical answer regardless.

The remaining calls run concurrently (:data:`RANK_CONCURRENCY`). They are pure
network work -- :func:`rank_candidates` touches no database -- so the threads
need no connection of their own, which is what makes this safe inside the
request's transaction.

Everything degrades rather than fails: no API key, no network, a bad response,
no pgvector, no ``sentence-transformers`` -- retrieval order stands and the
proposal says so. A Suggest button that returns nothing because a third party is
down is worse than one that returns a decent guess a curator can correct.
"""
import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Case, CharField, Count, F, Max, Q, Value, When
from django.db.models.functions import Upper

from omop_core.models import (
    Concept,
    ConceptEmbedding,
    ConceptSynonym,
    SourceCodeConceptMapping,
    UmlsSourceCode,
)

from omop_core.mapping.code_resolution import (
    CLINICAL_TABLES,
    NO_MATCHING_CONCEPT_ID,
    SOURCE_CODE_MAX,
    _QUARANTINE_TARGETS,
)

logger = logging.getLogger(__name__)

# A curator cannot review 10,483 codes. On staging 4,553 of them (43%) appear
# exactly once -- free text like 't(11;14)(CCND1,IGH) % in Bone Marrow by FISH',
# real findings but not codes anyone meets twice -- while 512 carry the traffic.
# Proposing for the long tail buries the codes that matter, so the default asks
# for ten sightings and the caller can lower it once the queue is drained.
DEFAULT_MIN_OCCURRENCES = 10

# Increment this whenever a material suggestion-algorithm change is released.
SUGGESTION_MODEL_VERSION = 'v0.2'
SUGGESTION_PROVENANCE = f'suggest {SUGGESTION_MODEL_VERSION}'

# How many trigram survivors lexical retrieval hands the reranker. Ten: enough
# that the right concept is in the list (it was third in the motivating
# example), few enough that reranking, the ranker's prompt and the embedding
# precompute are all bounded by it. The Code Mapping page exposes it next to the
# Lexical checkbox, because it is the one setting that trades recall against the
# cost of every stage after it.
CANDIDATE_LIMIT = 10

# A ceiling on what the UI may ask for. The shortlist is sent to the ranker in
# one prompt, so an unbounded value is a way to spend an unbounded number of
# tokens per source code.
LEXICAL_LIMIT_MAX = 100

# Ranking calls run concurrently. They are network-bound (4-6s each, measured)
# and touch no database, so the workers need no connection of their own -- which
# is the only reason threads are safe here: a thread that opened its own
# connection would not see the caller's open transaction.
RANK_CONCURRENCY = 8

# Below this a trigram hit is noise. Tuned against the staging corpus: the
# motivating example's correct answer scored 0.64 and its worst plausible
# candidate 0.59.
MIN_TRIGRAM_SCORE = 0.3

# A synonym match beats a name match at equal similarity. Synonyms are what
# clinicians write, and a source value is a clinician's words.
SYNONYM_BONUS = 0.05

# ---------------------------------------------------------------------------
# UMLS root-source mapping
# ---------------------------------------------------------------------------
# Maps OMOP vocabulary_id → UMLS SAB (root_source in umls_source_code).
# Verified against staging data (195 distinct root_source values).
VOCAB_TO_UMLS_ROOT = {
    'SNOMED': 'SNOMEDCT_US',
    'ICD10CM': 'ICD10CM',
    'ICD10': 'ICD10CM',       # HT-One ICD-10 codes are ICD-10-CM format
    'ICD10PCS': 'ICD10PCS',
    'LOINC': 'LNC',
    'RxNorm': 'RXNORM',
    'CPT4': 'CPT',
    'HCPCS': 'HCPCS',
    'NDC': 'NDC',
    'CVX': 'CVX',
    'ICD9CM': 'ICD9CM',
    'MeSH': 'MSH',
    'NDFRT': 'MED-RT',
}

# Reverse: UMLS SAB → OMOP vocabulary_id (for sibling-code lookups).
# Multiple OMOP vocabs can map to the same UMLS SAB (ICD10CM and ICD10 both
# map to ICD10CM SAB).  When that happens, prefer the canonical OMOP vocab
# (ICD10CM over ICD10) — first-seen wins, so iterate forward and skip dupes.
_UMLS_ROOT_TO_VOCAB: dict[str, str] = {}
for _k, _v in VOCAB_TO_UMLS_ROOT.items():
    _UMLS_ROOT_TO_VOCAB.setdefault(_v, _k)
assert _UMLS_ROOT_TO_VOCAB.get('ICD10CM') == 'ICD10CM', (
    "ICD10CM must appear before ICD10 in VOCAB_TO_UMLS_ROOT so the reverse "
    "map prefers the canonical Athena vocabulary for sibling lookups."
)

# ---------------------------------------------------------------------------
# Strategy labels
# ---------------------------------------------------------------------------
STRATEGY_UMLS = 'umls'
STRATEGY_VECTORS = 'vectors'
STRATEGY_LEXICAL = 'lexical'
ALL_STRATEGIES = [STRATEGY_UMLS, STRATEGY_VECTORS, STRATEGY_LEXICAL]


def _find_source_concept(source_vocabulary_id, source_code):
    """Look up the OMOP Concept for a source code, with ICD10CM_MERGE fallback.

    ICD-10 (HT-One) codes are ICD-10-CM format (#1028), but Athena loads
    concepts under vocabulary_id='ICD10CM'.  When the literal vocabulary has
    no concept, try the merged-vocabulary alias so the source_concept and its
    concept_name are still available for ranking and display.
    """
    if not source_vocabulary_id:
        return None
    concept = Concept.objects.filter(
        vocabulary_id=source_vocabulary_id,
        concept_code__iexact=source_code,
    ).first()
    if concept is not None:
        return concept
    # Fallback: try the canonical vocabulary this one merges into (or from).
    from omop_core.services.source_vocabularies import ICD10CM_MERGE
    # ICD10 → try ICD10CM
    canonical = ICD10CM_MERGE.get(source_vocabulary_id)
    if canonical:
        return Concept.objects.filter(
            vocabulary_id=canonical,
            concept_code__iexact=source_code,
        ).first()
    # ICD10CM → try ICD10 (reverse direction, less likely but symmetric)
    for alias, canon in ICD10CM_MERGE.items():
        if canon == source_vocabulary_id:
            hit = Concept.objects.filter(
                vocabulary_id=alias,
                concept_code__iexact=source_code,
            ).first()
            if hit:
                return hit
    return None


def umls_candidates(source_code, source_vocabulary_id, domain_id=None):
    """Find standard OMOP concepts via UMLS CUI bridging.

    Given a source code and its vocabulary, look up the UMLS CUI, then find
    all sibling codes across vocabularies that map to standard OMOP concepts.

    Returns a list of candidate dicts (same shape as lexical_candidates) plus
    metadata.  When a single standard concept is found the caller can skip the
    ranker -- UMLS equivalencies are curated by NLM.
    """
    umls_root = VOCAB_TO_UMLS_ROOT.get(source_vocabulary_id)
    if not umls_root:
        return [], None

    # 1. Find the CUI(s) for this source code.
    source_rows = (
        UmlsSourceCode.objects
        .filter(root_source=umls_root, code=source_code)
        .values_list('concept_id', flat=True)      # concept_id = CUI FK
        .distinct()
    )
    cuis = list(source_rows)
    if not cuis:
        return [], None

    # 2. Find sibling codes across all vocabularies sharing any of those CUIs.
    siblings = (
        UmlsSourceCode.objects
        .filter(concept_id__in=cuis)
        .exclude(root_source=umls_root, code=source_code)
        .values_list('root_source', 'code')
        .distinct()
    )

    # 3. Batch-lookup standard OMOP concepts for all siblings at once.
    lookup_pairs = []
    for sab, sibling_code in siblings:
        omop_vocab = _UMLS_ROOT_TO_VOCAB.get(sab)
        if omop_vocab:
            lookup_pairs.append(Q(vocabulary_id=omop_vocab, concept_code=sibling_code))

    candidates = []
    if lookup_pairs:
        q = lookup_pairs[0]
        for p in lookup_pairs[1:]:
            q |= p
        qs = Concept.objects.filter(
            q, standard_concept='S', invalid_reason__isnull=True,
        )
        if domain_id:
            qs = qs.filter(domain_id=domain_id)
        for c in qs[:CANDIDATE_LIMIT]:
            candidates.append({
                'concept_id': c.concept_id,
                'concept_name': c.concept_name,
                'concept_code': c.concept_code,
                'vocabulary_id': c.vocabulary_id,
                'concept_class_id': c.concept_class_id,
                'umls_score': 1.0,  # curated equivalency — max confidence
                'retrieval': STRATEGY_UMLS,
            })

    cui_str = ','.join(cuis) if len(cuis) <= 5 else f'{cuis[0]}...(+{len(cuis)-1})'
    return candidates, cui_str


def vector_rerank(source_value, candidates):
    """Reorder a retrieved shortlist by embedding similarity to *source_value*.

    Returns ``(candidates, applied)``.  ``applied`` is False whenever the
    ordering could not be improved -- no ``sentence-transformers``, no
    ``concept_embedding`` rows, a query too short to embed -- and the caller
    keeps the retrieval order it already had.

    Vectors were previously a *retrieval* tier, cosine-scanning every stored
    embedding in the domain (1.5M rows on staging, 2.6-2.9s per source code) to
    build a rival shortlist that then needed its own ranker call.  That is the
    expensive half of the job and the half embeddings are worst at: an ANN scan
    over a whole domain is a coarse filter, and it discarded the trigram
    evidence entirely.  Ordering is what embeddings are good at, and ordering a
    list this short costs one query embedding plus a primary-key lookup.

    Candidates with no stored embedding keep their retrieval order *below* every
    scored one.  Demoting them is deliberate: a missing embedding says the
    concept was not in the corpus when it was built, not that it is a poor
    match, but the scored ones have positive evidence and it is the ranker's
    prompt they are competing for.
    """
    if len(candidates) < 2:
        return candidates, False
    query = (source_value or '').strip()
    if len(query) < 3:
        return candidates, False

    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer  # noqa: F401
    except ImportError:
        logger.info('sentence-transformers not installed; vector reranking unavailable.')
        return candidates, False

    try:
        stored = dict(
            ConceptEmbedding.objects
            .filter(concept_id__in=[c['concept_id'] for c in candidates])
            .values_list('concept_id', 'embedding')
        )
    except Exception:                             # noqa: BLE001 - degrade, never fail
        logger.info('Vector reranking unavailable (pgvector or concept_embedding missing).')
        return candidates, False
    if not stored:
        return candidates, False

    try:
        query_vec = np.asarray(_get_embedding_model().encode(query), dtype='float32')
    except Exception:                             # noqa: BLE001 - degrade, never fail
        logger.warning('Could not embed %r for reranking.', query[:80])
        return candidates, False
    query_norm = float(np.linalg.norm(query_vec)) or 1.0

    scored, unscored = [], []
    for position, candidate in enumerate(candidates):
        vector = stored.get(candidate['concept_id'])
        if vector is None:
            unscored.append((position, candidate))
            continue
        vector = np.asarray(vector, dtype='float32')
        norm = float(np.linalg.norm(vector)) or 1.0
        candidate['vector_score'] = round(
            float(np.dot(query_vec, vector)) / (query_norm * norm), 4,
        )
        scored.append((position, candidate))

    # Position breaks ties so the order stays deterministic when two concepts
    # embed identically -- which happens, because concept names repeat across
    # vocabularies.
    scored.sort(key=lambda pair: (-pair[1]['vector_score'], pair[0]))
    return [c for _position, c in scored] + [c for _position, c in unscored], True


# Singleton for the embedding model -- loading it is expensive (~1s) and ~130MB
# in memory, so concurrent workers must not duplicate the load.
_embedding_model = None
_embedding_lock = threading.Lock()


def _get_embedding_model():
    """Return a cached SentenceTransformer instance (thread-safe)."""
    global _embedding_model
    if _embedding_model is None:
        with _embedding_lock:
            if _embedding_model is None:  # double-check after acquiring lock
                from sentence_transformers import SentenceTransformer
                _embedding_model = SentenceTransformer('BAAI/bge-small-en-v1.5')
    return _embedding_model


def vocabulary_aliases(source_vocabulary_id):
    """Every source vocabulary a tab covers, including merged aliases.

    The ICD10 tab shows rows stored under both ``ICD10`` and ``ICD10CM``: HT-One
    sends ICD-10 codes in ICD-10-CM format (#1028) and Athena loads the concepts
    under the canonical name.  Filtering on the tab's own id alone hides half
    the tab's rows from whatever is doing the filtering.
    """
    from omop_core.services.source_vocabularies import ICD10CM_MERGE
    vocab_ids = {source_vocabulary_id}
    for alias, canonical in ICD10CM_MERGE.items():
        if canonical == source_vocabulary_id:
            vocab_ids.add(alias)
    return vocab_ids


def suggestable_mappings(omop_table=None, *, source_vocabulary_id=None,
                         min_occurrences=DEFAULT_MIN_OCCURRENCES,
                         limit=None, resuggest=False):
    """The queue rows on one tab that a Suggest run is allowed to write to.

    This is the whole candidate set: Suggest reads the tab, and the tab is
    ``source_code_concept_mapping``.  Three filters decide it.

    **Provenance empty, or beginning with ``suggest``.**  Those are the rows
    whose destination nobody but a previous Suggest run has ever set.  A row
    stamped ``HT-One``, ``HT-FHIR``, ``athena`` or ``hk-labs`` carries a
    destination its importer asserted from more than the source text -- on
    staging that is 75,257 of 85,318 rows -- and re-deriving it here would
    overwrite a better answer with a worse one, at the cost of a model call each.

    **``proposed`` only.**  ``approved`` is a curator's sign-off and ``rejected``
    is equally a decision; re-proposing a rejected code put it back at the front
    of the queue on every run, where it spent a model call and created nothing.

    **No destination yet**, unless *resuggest*.  A row that already has a
    suggestion does not need another one.  *resuggest* is what the page's
    "Replace Current Suggestions" asks for, and it is the only way a model
    version bump reaches rows the previous version already answered.

    Ordered by occurrence, because that is the order a curator should meet them
    in: the code seen 400 times is worth more of their attention than the one
    seen once.  ``min_occurrences <= 1`` drops the filter rather than comparing
    against 1, so rows seeded with no count at all still appear.
    """
    rows = (
        SourceCodeConceptMapping.objects
        .filter(status='proposed')
        .filter(Q(origin_system='') | Q(origin_system__istartswith='suggest'))
        .select_related('source_concept')
    )
    # None means every clinical table, which is what the embedding precompute
    # walks; a Suggest run always names one.
    if omop_table is not None:
        rows = rows.filter(omop_table=omop_table)
    if source_vocabulary_id is not None:
        rows = rows.filter(source_vocabulary_id__in=vocabulary_aliases(source_vocabulary_id))
    if not resuggest:
        rows = rows.filter(target_concept__isnull=True)
    if min_occurrences > 1:
        rows = rows.filter(occurrence_count__gte=min_occurrences)
    rows = rows.order_by('-occurrence_count', 'source_code', 'id')
    return list(rows[:limit] if limit else rows)


def unmapped_source_values(omop_table, min_occurrences=DEFAULT_MIN_OCCURRENCES,
                           limit=None, source_vocabulary_id=None):
    """Source values at concept 0 that have no queue row at all.

    Not part of Suggest.  This is the *enqueue* half of the job, and it is a
    full group-by of a clinical table minus every existing mapping -- 4-7s per
    table on staging, before any candidate is retrieved.  Ingest already creates
    a queue row for every code it meets, so what this finds is the residue from
    before the resolver existed.  ``manage.py enqueue_unmapped_source_codes``
    runs it as the batch job it is; a web request must not.

    A source value is identified by both its text and source vocabulary.  The
    same text is valid in multiple code systems, and combining them would both
    lose FHIR provenance and create a mapping that could re-point the wrong
    facts.  ``''`` is reserved for genuinely uncoded rows.

    Ordered by how often they occur, because that is the order a curator should
    meet them in: the code seen 400 times is worth more of their attention than
    the one seen once.
    """
    model, concept_col, source_col = CLINICAL_TABLES[omop_table]
    source_concept_col = source_col.replace('_source_value', '_source_concept_id')
    source_vocabulary = Case(
        When(
            Q(**{f'{source_concept_col}__isnull': True})
            | Q(**{source_concept_col: NO_MATCHING_CONCEPT_ID}),
            then=Value(''),
        ),
        default=F(f'{source_concept_col}__vocabulary_id'),
        output_field=CharField(),
    )

    # Rejected counts as decided. Excluding it here put the code back at the
    # front of the queue on every run -- it sorts by occurrence -- where it
    # spent a model call and created nothing, and the caller reported
    # "no unmapped codes" because nothing was created.
    already = {
        ((vocabulary_id or ''), code.upper())
        for vocabulary_id, code in SourceCodeConceptMapping.objects.values_list(
            'source_vocabulary_id', 'source_code',
        )
    }

    rows = (
        model.objects
        .filter(**{concept_col: NO_MATCHING_CONCEPT_ID})
        .exclude(**{f'{source_col}__isnull': True})
        .exclude(**{source_col: ''})
        .annotate(source_vocabulary_id=source_vocabulary)
        .values(source_col, 'source_vocabulary_id')
        .annotate(occurrences=Count(model._meta.pk.name))
        .filter(occurrences__gte=min_occurrences)
        .order_by('-occurrences', source_col, 'source_vocabulary_id')
    )
    # When filtering by source vocabulary, only return rows from that vocabulary.
    # Expand merged vocabularies (e.g. ICD10 → [ICD10, ICD10CM]) so the merged
    # tab sees clinical rows from both the canonical and aliased vocab.
    if source_vocabulary_id is not None:
        rows = rows.filter(source_vocabulary_id__in=vocabulary_aliases(source_vocabulary_id))

    out = []
    for row in rows.iterator():
        value = row[source_col]
        row_vocab = row['source_vocabulary_id'] or ''
        if (row_vocab, value.upper()) in already:
            continue
        out.append((value, row_vocab, row['occurrences']))
        if limit and len(out) >= limit:
            break
    return out


def lexical_candidates(source_value, domain_id, limit=CANDIDATE_LIMIT):
    """Concepts whose name or synonyms look like this source value.

    Scoped to the domain, so a lab name cannot retrieve a drug. Standard
    concepts only -- a curator re-pointing at a non-standard one is a decision
    they can still make by hand, but it is never what we should suggest.
    """
    query = (source_value or '').strip().upper()
    if len(query) < 3:
        return []

    # Narrow with `%` first, score second.
    #
    # TrigramSimilarity(...) > x compiles to SIMILARITY(...) > x, which is not
    # an indexable expression -- it seq-scans 2.4M synonym rows, measured at
    # 4.49s for a single source value. `__trigram_similar` emits the `%`
    # operator, which is what gin_trgm_ops answers, so the GIN index does the
    # narrowing and similarity() only scores the handful that survive.
    #
    # The `%` must be applied to UPPER(col), not the raw column: both indexes
    # are on the uppercased expression, and querying the raw column silently
    # misses them -- the same raw-vs-UPPER mismatch that made concepts/search
    # ineffective (#262).
    #
    # `%` uses pg_trgm.similarity_threshold (0.3 by default), the same cut
    # MIN_TRIGRAM_SCORE applies -- the explicit filter stays so the constant
    # governs regardless of the session setting.
    by_name = (
        Concept.objects
        .filter(standard_concept='S', domain_id=domain_id, invalid_reason__isnull=True)
        .annotate(name_upper=Upper('concept_name'))
        .filter(name_upper__trigram_similar=query)
        .annotate(score=TrigramSimilarity(Upper('concept_name'), query))
        .filter(score__gt=MIN_TRIGRAM_SCORE)
        .order_by('-score')[:limit]
    )

    # Synonyms are a separate index and a separate signal; merged by concept,
    # keeping whichever route scored higher.
    synonym_hits = (
        ConceptSynonym.objects
        .annotate(name_upper=Upper('concept_synonym_name'))
        .filter(name_upper__trigram_similar=query)
        .annotate(score=TrigramSimilarity(Upper('concept_synonym_name'), query))
        .filter(score__gt=MIN_TRIGRAM_SCORE)
        .values('concept_id')
        .annotate(score=Max('score'))
        .order_by('-score')[:limit]
    )
    synonym_scores = {h['concept_id']: h['score'] + SYNONYM_BONUS for h in synonym_hits}

    merged = {}
    for concept in by_name:
        merged[concept.concept_id] = (concept, float(concept.score))
    if synonym_scores:
        for concept in Concept.objects.filter(
            concept_id__in=list(synonym_scores),
            standard_concept='S', domain_id=domain_id, invalid_reason__isnull=True,
        ):
            score = float(synonym_scores[concept.concept_id])
            if concept.concept_id not in merged or score > merged[concept.concept_id][1]:
                merged[concept.concept_id] = (concept, score)

    ranked = sorted(merged.values(), key=lambda pair: -pair[1])[:limit]
    return [
        {
            'concept_id': c.concept_id,
            'concept_name': c.concept_name,
            'concept_code': c.concept_code,
            'vocabulary_id': c.vocabulary_id,
            'concept_class_id': c.concept_class_id,
            'lexical_score': round(score, 3),
            'retrieval': STRATEGY_LEXICAL,
        }
        for c, score in ranked
    ]


_RANKING_SCHEMA = {
    'type': 'object',
    'properties': {
        'concept_id': {
            'type': ['integer', 'null'],
            'description': 'The best candidate, or null if none of them is right.',
        },
        'confidence': {'type': 'string', 'enum': ['high', 'medium', 'low']},
        'reason': {'type': 'string', 'description': 'One sentence, for the curator.'},
    },
    'required': ['concept_id', 'confidence', 'reason'],
    'additionalProperties': False,
}

_RANKING_SYSTEM = """You map clinical source codes onto OMOP concepts.

You are given one source value as it appeared in real clinical data, and a
shortlist of candidate OMOP concepts retrieved by string similarity. Pick the
candidate that means the same clinical thing, or null if none does.

String similarity is not meaning. The highest-scoring candidate is often wrong
in a specific way: a ratio is not the analyte it is computed from, a panel is
not one of its components, a urine measurement is not a serum one, and a
qualitative finding is not a quantitative result. Prefer the candidate whose
specimen, quantity and method match the source value; where the source value is
silent on method, prefer the more general concept over a method-specific one.

Answer null rather than guessing. A wrong mapping is written into patient
records; an unmapped code stays in a queue where a human will see it."""


def rank_candidates(source_value, candidates, source_description=''):
    """Re-rank a lexical shortlist by meaning. Returns (chosen, note).

    ``chosen`` is a candidate dict or None; ``note`` explains the choice for the
    curator, including when the model was unavailable and the lexical order
    stands.
    """
    if not candidates:
        return None, 'No candidate concept scored above the similarity threshold.'

    top = candidates[0]
    top_score = (
        top.get('lexical_score')
        or top.get('vector_score')
        or top.get('umls_score')
        or '?'
    )
    fallback_note = (
        f'Best-match fallback (score {top_score}). '
        f'Ranking model unavailable, so this is the highest retrieval score, '
        f'which is frequently not the closest clinical match — review carefully.'
    )

    if not getattr(settings, 'ANTHROPIC_API_KEY', ''):
        return top, fallback_note

    try:
        import anthropic
    except ImportError:
        logger.warning('anthropic SDK not installed; falling back to lexical order.')
        return top, fallback_note

    listing = '\n'.join(
        f'{c["concept_id"]}\t{c["vocabulary_id"]}:{c["concept_code"]}\t'
        f'{c["concept_name"]}\t(class {c["concept_class_id"]})'
        for c in candidates
    )
    described = f'\nSource description: {source_description}' if source_description else ''

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model='claude-opus-5',
            # Thinking tokens count against this. At 1024 the response stopped
            # at max_tokens with no text block, json.loads raised, and the
            # ranker silently degraded to the lexical order it exists to fix.
            max_tokens=16000,
            system=_RANKING_SYSTEM,
            thinking={'type': 'adaptive'},
            output_config={
                'effort': 'medium',
                'format': {'type': 'json_schema', 'schema': _RANKING_SCHEMA},
            },
            messages=[{
                'role': 'user',
                'content': (
                    f'Source value: {source_value}{described}\n\n'
                    f'Candidates (concept_id, vocabulary:code, name, class):\n{listing}'
                ),
            }],
        )
    except Exception as exc:                      # noqa: BLE001 - degrade, never fail
        # A Suggest button that returns nothing because a third party is down is
        # worse than one that returns a decent guess a curator can correct.
        logger.warning('Concept ranking failed for %r: %s', source_value, exc)
        return top, fallback_note

    payload = next(
        (block.text for block in response.content if block.type == 'text'), ''
    )
    try:
        verdict = json.loads(payload)
    except (TypeError, ValueError):
        verdict = None
    # A bare `null` or a list parses fine and then has no .get -- and the system
    # prompt asks for null, so this is the shape a model most plausibly gets
    # wrong. Degrading is the contract; 500ing the request is not.
    if not isinstance(verdict, dict):
        logger.warning('Concept ranking returned unusable output for %r.', source_value)
        return top, fallback_note

    chosen_id = verdict.get('concept_id')
    if chosen_id is None:
        return None, f'No suitable concept: {verdict.get("reason", "")}'.strip()

    chosen = next((c for c in candidates if c['concept_id'] == chosen_id), None)
    if chosen is None:
        # The model named something outside the shortlist. Do not follow it --
        # the candidates were domain-scoped and validated, an arbitrary id is not.
        logger.warning(
            'Concept ranking chose %s, which was not among the candidates for %r.',
            chosen_id, source_value,
        )
        return top, fallback_note

    return chosen, (
        f'{verdict.get("confidence", "unknown")} confidence: '
        f'{verdict.get("reason", "")}'.strip()
    )


def retrieval_pool(*, source_code, source_vocabulary_id, source_text, domain_id,
                   strategies, lexical_limit=CANDIDATE_LIMIT):
    """Candidates for one source code, in the order the ranker should see them.

    Returns ``(candidates, umls_cui, definitive)``.  ``definitive`` means UMLS
    bridged the code to exactly one standard concept: an NLM-curated
    equivalency, so the pipeline stops there and spends no model call.
    """
    candidates, umls_cui = [], None

    if STRATEGY_UMLS in strategies:
        umls_hits, umls_cui = umls_candidates(source_code, source_vocabulary_id, domain_id)
        if len(umls_hits) == 1:
            return umls_hits, umls_cui, True
        candidates = list(umls_hits)

    if STRATEGY_LEXICAL in strategies:
        seen = {c['concept_id'] for c in candidates}
        # UMLS hits stay ahead of lexical ones and are never displaced by a
        # lexical duplicate: a curated equivalency outranks a string overlap,
        # and its umls_score is the evidence the ranker's prompt shows.
        candidates += [
            hit for hit in lexical_candidates(
                source_text or source_code, domain_id, limit=lexical_limit,
            )
            if hit['concept_id'] not in seen
        ]

    if STRATEGY_VECTORS in strategies:
        candidates, _reranked = vector_rerank(source_text or source_code, candidates)

    return candidates, umls_cui, False


def _prepare(*, source_code, source_vocabulary_id, source_text, domain_id,
             strategies, lexical_limit):
    """Everything for one source code that needs the database, and nothing more.

    Split out so the ranking that follows is pure network work and can be run
    concurrently without a database connection per thread.
    """
    candidates, umls_cui, definitive = retrieval_pool(
        source_code=source_code, source_vocabulary_id=source_vocabulary_id,
        source_text=source_text, domain_id=domain_id,
        strategies=strategies, lexical_limit=lexical_limit,
    )
    job = {
        'candidates': candidates,
        'umls_cui': umls_cui,
        'source_code': source_code,
        'source_text': source_text,
        'chosen': None,
        'note': '',
        'strategy_used': None,
        'vector_reranked': any('vector_score' in c for c in candidates),
    }
    if definitive:
        job['chosen'] = candidates[0]
        job['strategy_used'] = STRATEGY_UMLS
        job['note'] = f'UMLS CUI bridge ({umls_cui}): exact cross-vocabulary equivalency.'
    return job


def rank_jobs(jobs):
    """Fill in ``chosen``/``note`` for every job still needing the ranker.

    Concurrent because each call is 4-6s of waiting on a third party and there
    are up to ``SUGGEST_MAX_PER_RUN`` of them.  :func:`rank_candidates`
    reads no database, so the workers open no connection -- a thread that did
    would be outside the caller's transaction and could not see rows it has not
    committed.
    """
    pending = [job for job in jobs if job['chosen'] is None and job['candidates']]
    for job in jobs:
        if job['chosen'] is None and not job['candidates']:
            job['note'] = 'No candidate concept found by any enabled strategy.'

    def rank(job):
        return rank_candidates(
            job['source_code'], job['candidates'],
            source_description=job['source_text'],
        )

    def record(job, chosen, note):
        job['chosen'], job['note'] = chosen, note
        if chosen is not None:
            job['strategy_used'] = chosen.get('retrieval') or STRATEGY_LEXICAL

    if len(pending) <= 1:
        for job in pending:
            record(job, *rank(job))
        return jobs

    with ThreadPoolExecutor(max_workers=min(RANK_CONCURRENCY, len(pending))) as pool:
        futures = {pool.submit(rank, job): job for job in pending}
        for future in as_completed(futures):
            job = futures[future]
            try:
                chosen, note = future.result()
            except Exception as exc:              # noqa: BLE001 - degrade, never fail
                # rank_candidates already swallows its own failures; this is the
                # backstop for anything that escapes it, so one bad code cannot
                # take down a whole Suggest run.
                logger.warning('Ranking raised for %r: %s', job['source_code'], exc)
                chosen, note = None, 'Ranking failed; no destination proposed.'
            record(job, chosen, note)
    return jobs


def suggest_source_code(*, source_vocabulary_id, source_code, source_text, omop_table):
    """Return the best proposed destination for one unresolved source code.

    This is the single-code entry point for the canonical lookup API.  It owns
    the choice of retrieval/ranking strategies; callers only receive a
    standard Concept suitable for a *proposed* SCCM row, never an approved
    resolution.  The multi-strategy implementation extends this function, so
    import adapters do not need to know whether the service used UMLS, vectors,
    lexical retrieval, or the ranker.
    """
    target = _QUARANTINE_TARGETS.get(omop_table)
    if target is None:
        return None, ''
    _hk_vocabulary, domain_id, _concept_class_id, _slug_prefix = target
    source_concept = _find_source_concept(source_vocabulary_id, source_code)
    description = source_text or (source_concept.concept_name if source_concept else '')
    candidates = lexical_candidates(description or source_code, domain_id)
    chosen, note = rank_candidates(
        description or source_code,
        candidates,
        source_description=description,
    )
    if chosen is None:
        return None, note
    return Concept.objects.filter(concept_id=chosen['concept_id']).first(), note


def _source_description(mapping, source_concept):
    """Return ``(description, umls_preferred_name)`` for one queue row.

    The UMLS preferred term is looked up whether or not it is needed for the
    description: it is the vocabulary's own canonical name for the code, shown
    read-only beside the row, so it is worth storing on its own account.

    Description preference is evidence order.  The mapping's own description is
    what the importer sent.  A loaded source concept's name is the vocabulary's
    words for the code, which makes ranking a code such as ``85319-5``
    meaningful without pretending the code is a display name.  The UMLS term is
    the same idea one bridge further out.
    """
    umls_name = mapping.umls_source_name or ''
    if not umls_name:
        umls_root = VOCAB_TO_UMLS_ROOT.get(mapping.source_vocabulary_id or '')
        if umls_root:
            umls_name = (
                UmlsSourceCode.objects
                .filter(root_source=umls_root, code=mapping.source_code, is_preferred=True)
                .values_list('name', flat=True)
                .first()
            ) or ''

    description = (
        mapping.source_code_description
        or (source_concept.concept_name if source_concept else '')
        or umls_name
    )
    return description, umls_name


def suggest_mappings(omop_table, *, min_occurrences=DEFAULT_MIN_OCCURRENCES,
                     limit=None, dry_run=False, source_vocabulary_id=None,
                     strategies=None, lexical_limit=CANDIDATE_LIMIT,
                     resuggest=False, progress=None):
    """Propose destinations for the unanswered queue rows on one tab.

    The candidate set is :func:`suggestable_mappings` -- rows already on the
    tab whose provenance is empty or begins with ``suggest``.  Nothing is
    created: ingest created these rows, and Suggest fills in the destination
    they are missing.  Where no candidate is convincing the row keeps no
    destination, because minting an HK-* concept named after the source code
    would create a fake destination with no clinical meaning.

    *strategies* controls the pipeline, which is not a waterfall of independent
    tiers but one retrieval and one ranking:

    - ``umls`` — CUI bridge.  A single standard concept ends it with no model call.
    - ``lexical`` — GIN trigram, the best *lexical_limit* survivors.
    - ``vectors`` — reorders those survivors by embedding similarity.

    *progress*, when given, is called as ``progress(stage, done, total)`` with
    *stage* ``'retrieving'`` then ``'writing'``.  Retrieval is two thirds of the
    run and completes for every code before the first destination is written, so
    a caller reporting only writes would show nothing at all for most of the
    wait.

    Returns a list of result dicts, one per row considered.
    """
    if strategies is None:
        strategies = list(ALL_STRATEGIES)
    lexical_limit = max(1, min(int(lexical_limit or CANDIDATE_LIMIT), LEXICAL_LIMIT_MAX))

    target = _QUARANTINE_TARGETS.get(omop_table)
    if target is None:
        raise ValueError(f'No quarantine vocabulary for table {omop_table!r}.')
    _hk_vocabulary, domain_id, _concept_class_id, _slug_prefix = target

    mappings = suggestable_mappings(
        omop_table, source_vocabulary_id=source_vocabulary_id,
        min_occurrences=min_occurrences, limit=limit, resuggest=resuggest,
    )

    def report(stage, done):
        if progress is not None:
            progress(stage, done, len(mappings))

    report('retrieving', 0)

    # Phase 1 -- everything that reads the database, serially.
    jobs = []
    for mapping in mappings:
        source_concept = mapping.source_concept or _find_source_concept(
            mapping.source_vocabulary_id, mapping.source_code,
        )
        description, umls_source_name = _source_description(mapping, source_concept)
        job = _prepare(
            source_code=mapping.source_code,
            source_vocabulary_id=mapping.source_vocabulary_id,
            source_text=description,
            domain_id=mapping.domain_id or domain_id,
            strategies=strategies,
            lexical_limit=lexical_limit,
        )
        job['mapping'] = mapping
        job['source_concept'] = source_concept
        job['source_description'] = description
        job['umls_source_name'] = umls_source_name
        jobs.append(job)
        report('retrieving', len(jobs))

    # Phase 2 -- the ranking calls, concurrently, touching no database.
    rank_jobs(jobs)
    report('writing', 0)

    # Phase 3 -- the writes, serially.
    from omop_core.services.athena_mapping_guard import (
        ATHENA_DUPLICATE_MESSAGE, athena_supplies_mapping,
    )
    results = []
    for job in jobs:
        mapping = job['mapping']
        chosen, note = job['chosen'], job['note']
        entry = {
            'source_code': mapping.source_code,
            'source_vocabulary_id': mapping.source_vocabulary_id,
            'source_code_description': job['source_description'],
            'occurrences': mapping.occurrence_count,
            'suggested': chosen,
            'note': note,
            'candidates_considered': len(job['candidates']),
            'strategy_used': job['strategy_used'],
            'vector_reranked': job['vector_reranked'],
            'umls_cui': job['umls_cui'],
            'mapping_id': mapping.id,
            'updated': False,
        }
        if chosen and athena_supplies_mapping(
            mapping.source_vocabulary_id, mapping.source_code[:SOURCE_CODE_MAX],
            chosen['concept_id'],
        ):
            entry.update(suggested=None, note=ATHENA_DUPLICATE_MESSAGE)
            results.append(entry)
            report('writing', len(results))
            continue
        if dry_run:
            results.append(entry)
            report('writing', len(results))
            continue

        concept = (
            Concept.objects.filter(concept_id=chosen['concept_id']).first()
            if chosen else None
        )
        mapping.target_concept = concept
        mapping.suggested_target_concept = concept
        mapping.destination_vocabulary_id = concept.vocabulary_id if concept else ''
        mapping.origin_system = SUGGESTION_PROVENANCE
        mapping.suggestion_model_version = SUGGESTION_MODEL_VERSION
        mapping.notes = note
        mapping.suggest_strategy = job['strategy_used'] or ''
        mapping.umls_cui = job['umls_cui'] or ''
        fields = [
            'target_concept', 'suggested_target_concept', 'destination_vocabulary_id',
            'origin_system', 'suggestion_model_version', 'notes', 'suggest_strategy',
            'umls_cui', 'updated_at',
        ]
        # Source-side enrichment is written only when it was missing: these
        # describe the code, not the suggestion, and a curator may have
        # corrected them.
        if job['source_concept'] is not None and mapping.source_concept_id is None:
            mapping.source_concept = job['source_concept']
            fields.append('source_concept')
        if job['umls_source_name'] and not mapping.umls_source_name:
            mapping.umls_source_name = job['umls_source_name'][:255]
            fields.append('umls_source_name')
        if job['source_description'] and not mapping.source_code_description:
            mapping.source_code_description = job['source_description'][:255]
            fields.append('source_code_description')
        mapping.save(update_fields=fields)
        entry['updated'] = True
        results.append(entry)
        report('writing', len(results))

    return results


def suggest_one_mapping(source_code, source_vocabulary_id, omop_table, *,
                        source_description='', strategies=None,
                        lexical_limit=CANDIDATE_LIMIT):
    """Run the same UMLS → lexical → vector-rerank pipeline for one dialog row."""
    if strategies is None:
        strategies = list(ALL_STRATEGIES)
    lexical_limit = max(1, min(int(lexical_limit or CANDIDATE_LIMIT), LEXICAL_LIMIT_MAX))
    target = _QUARANTINE_TARGETS.get(omop_table)
    if target is None:
        raise ValueError(f'No quarantine vocabulary for table {omop_table!r}.')
    _hk_vocabulary, domain_id, _class, _slug = target
    source_concept = _find_source_concept(source_vocabulary_id, source_code)
    description = source_description or (
        source_concept.concept_name if source_concept else ''
    )
    job = _prepare(
        source_code=source_code, source_vocabulary_id=source_vocabulary_id,
        source_text=description, domain_id=domain_id,
        strategies=strategies, lexical_limit=lexical_limit,
    )
    rank_jobs([job])

    from omop_core.services.athena_mapping_guard import (
        ATHENA_DUPLICATE_MESSAGE, athena_supplies_mapping,
    )
    chosen, note = job['chosen'], job['note']
    if chosen and athena_supplies_mapping(source_vocabulary_id, source_code,
                                          chosen['concept_id']):
        chosen, note = None, ATHENA_DUPLICATE_MESSAGE
    return {
        'suggested': chosen,
        'note': note or 'No candidate concept found by any enabled strategy.',
        'strategy_used': job['strategy_used'],
        'umls_cui': job['umls_cui'],
        'candidates_considered': len(job['candidates']),
        'vector_reranked': job['vector_reranked'],
    }

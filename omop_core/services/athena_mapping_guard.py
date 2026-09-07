"""Prevent redundant curator/suggestion pairs already supplied by Athena."""
from django.db.models.functions import Trim

from omop_core.models import SourceCodeConceptMapping
from omop_core.services import source_vocabularies

ATHENA_DUPLICATE_MESSAGE = 'This source and destination map is already supplied by Athena'


def source_tab_vocabularies(vocabulary_id):
    """The source systems represented by one curation tab."""
    if vocabulary_id in source_vocabularies.WEARABLE_SOURCE_VOCABULARIES:
        return source_vocabularies.WEARABLE_SOURCE_VOCABULARIES
    aliases = {
        **source_vocabularies.ICD10CM_MERGE,
        **source_vocabularies.VOCABULARY_OID_ALIASES,
    }
    canonical = aliases.get(vocabulary_id, vocabulary_id)
    return {canonical, *(alias for alias, target in aliases.items() if target == canonical)}


def athena_supplies_mapping(vocabulary_id, source_code, destination_id, *, exclude_id=None):
    if not destination_id or not source_code.strip():
        return False
    mappings = SourceCodeConceptMapping.objects.filter(
        source_vocabulary_id__in=source_tab_vocabularies(vocabulary_id),
        origin_system='athena', target_concept_id=destination_id,
    ).alias(trimmed_source_code=Trim('source_code')).filter(
        trimmed_source_code__iexact=source_code.strip(),
    )
    if exclude_id is not None:
        mappings = mappings.exclude(pk=exclude_id)
    return mappings.exists()

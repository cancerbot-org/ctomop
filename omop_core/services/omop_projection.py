"""Project PatientRecord edits into today's OMOP facts, retaining earlier days."""
import logging

from django.db import transaction
from django.utils import timezone

from omop_core.models import (
    ConditionOccurrence, DrugExposure, Measurement, Observation,
    PatientRecord, Person, ProcedureOccurrence,
)
from omop_core.services.pk import next_pk

logger = logging.getLogger(__name__)

# An explicit empty result stops derivation from falling back to older results.
CLEAR_VALUE = 'PatientRecord:cleared'

_TARGET_CONFIG = {
    'measurement': (
        Measurement, 'measurement_id', 'measurement_concept_id',
        'measurement_date', 'measurement_type_concept_id',
        'measurement_source_value', 'value_as_number', 'value_as_string',
    ),
    'observation': (
        Observation, 'observation_id', 'observation_concept_id',
        'observation_date', 'observation_type_concept_id',
        'observation_source_value', 'value_as_number', 'value_as_string',
    ),
    'condition': (
        ConditionOccurrence, 'condition_occurrence_id', 'condition_concept_id',
        'condition_start_date', 'condition_type_concept_id',
        'condition_source_value', None, None,
    ),
    'drug_exposure': (
        DrugExposure, 'drug_exposure_id', 'drug_concept_id',
        'drug_exposure_start_date', 'drug_type_concept_id',
        'drug_source_value', None, None,
    ),
    'procedure': (
        ProcedureOccurrence, 'procedure_occurrence_id', 'procedure_concept_id',
        'procedure_date', 'procedure_type_concept_id',
        'procedure_source_value', None, None,
    ),
}


def _is_empty(value):
    return value is None or value == '' or value == [] or value == {}


def projection_for_descriptor(entry):
    """Use the same recipe and value/unit semantics the editor advertises."""
    if not entry or not entry.get('writable') or entry.get('target') != 'patient_record':
        return None
    if not entry.get('projection'):
        return None
    return {
        **entry['projection'],
        'value_kind': entry.get('value_kind'),
        'unit': entry.get('unit') or entry['projection'].get('unit'),
    }


def project_field_to_omop(mapping) -> int:
    """Backfill pending user edits, not values already derived from OMOP.

    The pending-field list makes retries idempotent. Lock each record through
    projection and refresh, using the same lock as the PATCH handler.
    """
    from omop_core.services.patient_record_service import refresh_patient_record
    from omop_core.services.write_descriptor import build_writable_field_descriptor

    if mapping.status != 'approved':
        return 0
    projection = projection_for_descriptor(
        build_writable_field_descriptor().get(mapping.field_name)
    )
    if not projection:
        return 0
    records = PatientRecord.objects.filter(
        user_edited_fields__contains=[mapping.field_name],
    ).values_list('pk', flat=True)
    count = 0
    for record_id in records.iterator():
        try:
            with transaction.atomic():
                record = PatientRecord.objects.select_for_update().select_related('person').get(pk=record_id)
                if mapping.field_name not in (record.user_edited_fields or []):
                    continue
                if project_single_value(record.person, mapping.field_name,
                                        getattr(record, mapping.field_name), projection):
                    refresh_patient_record(record.person)
                    count += 1
        except Exception:
            logger.exception('Projection failed for record %s field %s', record_id, mapping.field_name)
    return count


def project_single_value(person, field_name, value, projection):
    """Update a matching non-erroneous fact today, or create today's fact.

    Matching includes the concept and source key. Earlier dates are history and
    are never updated. The person lock serializes concurrent first writes for a
    day; an atomic savepoint keeps projection failures from poisoning PATCH.
    """
    target = projection.get('omop_table')
    concept_id = projection.get('concept_id')
    source_value = projection.get('source_value')
    if target not in _TARGET_CONFIG or concept_id is None or not source_value:
        return False
    model, pk_field, concept_field, date_field, type_field, src_field, val_num, val_str = _TARGET_CONFIG[target]
    # Occurrence tables cannot encode a null/negative answer. Leave that edit
    # pending on PatientRecord instead of inventing an affirmative occurrence.
    if val_num is None and (_is_empty(value) or value is False):
        return False

    today = timezone.localdate()
    try:
        with transaction.atomic():
            Person.objects.select_for_update().get(pk=person.pk)
            instance = model.objects.filter(
                person=person, is_erroneous=False,
                **{concept_field: concept_id, src_field: source_value, date_field: today},
            ).order_by('-' + pk_field).first()
            existing = instance is not None
            if instance is None:
                instance = model(**{
                    pk_field: next_pk(model, pk_field), 'person': person,
                    concept_field: concept_id, src_field: source_value,
                    date_field: today, type_field: projection.get('type_concept_id') or 32817,
                })
            answer_fields = ('value_as_number', 'value_as_string', 'value_as_concept_id',
                             'value_source_value', 'unit_source_value', 'unit_concept_id')
            previous = {f: getattr(instance, f) for f in answer_fields} if val_num else {}
            if val_num is not None:
                # Reset all answer columns, including answers on same-day imports.
                instance.value_as_number = None
                instance.value_as_string = None
                instance.value_as_concept_id = None
                instance.value_source_value = CLEAR_VALUE if _is_empty(value) else None
                if not _is_empty(value):
                    kind = projection.get('value_kind')
                    if kind in ('string', 'date', 'json'):
                        instance.value_as_string = str(value)
                    else:
                        try:
                            instance.value_as_number = float(value)
                        except (ValueError, TypeError):
                            instance.value_as_string = str(value)
                instance.unit_source_value = projection.get('unit') or None
                instance.unit_concept_id = projection.get('unit_concept_id') or None
            if existing and all(getattr(instance, f) == v for f, v in previous.items()):
                return False
            instance._skip_patient_record_refresh = True
            instance.save()
        return True
    except Exception:
        logger.exception('Projection failed for person %s field %s', person.pk, field_name)
        return False


def without_cleared_history(rows, target):
    """Hide cleared results and their predecessors from derivation, not storage.

    Input is sorted newest first by date and ID. A later non-empty result is
    retained and becomes current even when a previous day was cleared.
    """
    _, _, concept_field, _, _, source_field, _, _ = _TARGET_CONFIG[target]
    cleared = set()
    result = []
    for row in rows:
        key = (getattr(row, concept_field), getattr(row, source_field))
        if row.value_source_value == CLEAR_VALUE:
            cleared.add(key)
        elif key not in cleared:
            result.append(row)
    return result

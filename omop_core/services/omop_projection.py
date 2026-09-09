"""Project PatientRecord values into OMOP tables.

Two entry points:

1. ``project_field_to_omop(mapping)`` — batch: when a curator approves a
   mapping, backfills all PatientRecords that already carry a user-edited value.

2. ``project_single_value(person, field_name, value, projection)`` — inline:
   called from the PatientRecord PATCH handler for fields that have approved
   mappings, so the OMOP fact is created at write time rather than waiting for
   a separate step.

Both upsert by (person_id, source_value) to avoid duplicates.
"""
import logging
from datetime import date

from django.db import transaction
from django.utils import timezone

from omop_core.models import (
    ConditionOccurrence, Concept, DrugExposure, Measurement,
    Observation, PatientRecord, ProcedureOccurrence,
)
from omop_core.services.pk import next_pk
from omop_core.services.write_descriptor import mapping_target_for

logger = logging.getLogger(__name__)

# concept_id 0 — used when no concept is resolved.
_ZERO_CONCEPT_ID = 0

# Mapping from target name to (Model, pk_field, concept_field, date_field,
# type_field, source_field, value_number_field, value_string_field)
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


def _omop_fact_exists(model, person_id, source_field, source_value):
    """Check if an OMOP fact already exists for this person + source_value."""
    return model.objects.filter(
        person_id=person_id,
        **{source_field: source_value},
    ).exists()


def project_field_to_omop(mapping) -> int:
    """Write PatientRecord values into OMOP for a newly approved mapping.

    Returns the count of OMOP facts created.
    """
    target = mapping_target_for(mapping.omop_table)
    if target is None or target not in _TARGET_CONFIG:
        return 0
    if not mapping.concept_id:
        return 0

    source_value = mapping.source_value or (
        mapping.concept.concept_code if mapping.concept else None
    )
    if not source_value:
        return 0

    config = _TARGET_CONFIG[target]
    model, pk_field, concept_field, date_field, type_field, src_field, val_num, val_str = config

    # Find PatientRecords with non-empty values for this field
    records = (
        PatientRecord.objects
        .exclude(**{mapping.field_name: None})
        .exclude(**{mapping.field_name: ''})
        .select_related('person')
    )

    # Ensure the concept exists
    try:
        concept = Concept.objects.get(concept_id=mapping.concept_id)
    except Concept.DoesNotExist:
        logger.warning(
            'project_field_to_omop: concept_id=%s not found for field %s',
            mapping.concept_id, mapping.field_name,
        )
        return 0

    # Type concept — default to 32817 (EHR) if not set
    type_concept_id = mapping.type_concept_id or 32817

    from omop_core.signals import suppress_patient_record_refresh

    created = 0
    persons_affected = set()

    with suppress_patient_record_refresh():
        for record in records.iterator():
            if _omop_fact_exists(model, record.person_id, src_field, source_value):
                continue

            value = getattr(record, mapping.field_name)
            if _is_empty(value):
                continue

            pk = next_pk(model, pk_field)
            kwargs = {
                pk_field: pk,
                'person_id': record.person_id,
                concept_field: mapping.concept_id,
                date_field: date.today(),
                type_field: type_concept_id,
                src_field: source_value,
            }

            # Set value columns if the target supports them
            if val_num is not None:
                try:
                    kwargs[val_num] = float(value) if value is not None else None
                except (ValueError, TypeError):
                    kwargs[val_num] = None
                    if val_str is not None:
                        kwargs[val_str] = str(value) if value is not None else None
            elif val_str is not None:
                kwargs[val_str] = str(value) if value is not None else None

            try:
                model.objects.create(**kwargs)
                created += 1
                persons_affected.add(record.person_id)
            except Exception:
                logger.exception(
                    'project_field_to_omop: failed to create %s for person %s field %s',
                    model.__name__, record.person_id, mapping.field_name,
                )

    # Refresh affected PatientRecords so derivation picks up the new facts
    # and cleans user_edited_fields.
    if persons_affected:
        from omop_core.models import Person
        from omop_core.services.patient_record_service import refresh_patient_record

        if len(persons_affected) > 100:
            logger.warning(
                'project_field_to_omop: %d persons affected for field %s — '
                'consider running as a Celery task',
                len(persons_affected), mapping.field_name,
            )
        for person_id in persons_affected:
            try:
                person = Person.objects.get(person_id=person_id)
                refresh_patient_record(person)
            except Person.DoesNotExist:
                pass
            except Exception:
                logger.exception(
                    'project_field_to_omop: refresh failed for person %s',
                    person_id,
                )

    logger.info(
        'project_field_to_omop: created %d %s rows for field %s (%d persons)',
        created, model.__name__, mapping.field_name, len(persons_affected),
    )
    return created


def project_single_value(person, field_name, value, projection):
    """Write one PatientRecord value into the OMOP table named by *projection*.

    Called from the PATCH handler when the field has an approved mapping.
    Upserts by (person_id, source_value): if the fact exists, updates its value;
    otherwise creates it.

    *projection* is the dict the write descriptor nests under the ``projection``
    key — it carries ``omop_table``, ``concept_id``, ``source_value``, etc.

    Returns True if a fact was created or updated, False if skipped.
    """
    target = projection.get('omop_table')
    if target not in _TARGET_CONFIG:
        logger.warning(
            'project_single_value: unknown target %r for field %s',
            target, field_name,
        )
        return False

    if _is_empty(value):
        return False

    concept_id = projection.get('concept_id')
    source_value = projection.get('source_value')
    if not concept_id or not source_value:
        return False

    config = _TARGET_CONFIG[target]
    model, pk_field, concept_field, date_field, type_field, src_field, val_num, val_str = config
    type_concept_id = projection.get('type_concept_id') or 32817

    # Upsert: update existing fact or create new one.
    existing = model.objects.filter(
        person_id=person.person_id,
        **{src_field: source_value},
    ).first()

    if existing:
        # Update value columns on the existing fact.
        updated = False
        if val_num is not None:
            try:
                new_num = float(value) if value is not None else None
            except (ValueError, TypeError):
                new_num = None
            if getattr(existing, val_num) != new_num:
                setattr(existing, val_num, new_num)
                updated = True
            if new_num is None and val_str is not None:
                new_str = str(value) if value is not None else None
                if getattr(existing, val_str) != new_str:
                    setattr(existing, val_str, new_str)
                    updated = True
        elif val_str is not None:
            new_str = str(value) if value is not None else None
            if getattr(existing, val_str) != new_str:
                setattr(existing, val_str, new_str)
                updated = True
        if updated:
            existing._skip_patient_record_refresh = True
            existing.save()
        return updated

    # Create new fact.
    pk = next_pk(model, pk_field)
    kwargs = {
        pk_field: pk,
        'person_id': person.person_id,
        concept_field: concept_id,
        date_field: date.today(),
        type_field: type_concept_id,
        src_field: source_value,
    }
    if val_num is not None:
        try:
            kwargs[val_num] = float(value) if value is not None else None
        except (ValueError, TypeError):
            kwargs[val_num] = None
            if val_str is not None:
                kwargs[val_str] = str(value) if value is not None else None
    elif val_str is not None:
        kwargs[val_str] = str(value) if value is not None else None

    try:
        instance = model(**kwargs)
        instance._skip_patient_record_refresh = True
        instance.save()
        return True
    except Exception:
        logger.exception(
            'project_single_value: failed to create %s for person %s field %s',
            model.__name__, person.person_id, field_name,
        )
        return False

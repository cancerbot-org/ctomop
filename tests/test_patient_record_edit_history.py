"""PatientRecord editor round trips preserve history and reuse today's facts."""
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from omop_core.models import FieldConceptMapping, Measurement, Observation
from omop_core.services.omop_projection import CLEAR_VALUE, project_field_to_omop
from omop_core.services.patient_record_service import refresh_patient_record
from omop_core.signals import suppress_patient_record_refresh
from patient_portal.models import Identity
from tests.factories import ConceptFactory, MeasurementFactory, PatientRecordFactory, VocabularyFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def editor(settings):
    settings.CELERY_BROKER_URL = ''
    ConceptFactory(concept_id=32865, concept_code='patient-report-type')
    record = PatientRecordFactory()
    client = APIClient()
    client.force_authenticate(Identity.objects.create_user(email='edit-history@example.test', is_staff=True))
    return record, client


def patch_field(editor, field, value):
    record, client = editor
    response = client.patch(f'/api/patient-info/{record.person_id}/', {field: value}, format='json')
    assert response.status_code == 200, response.data
    record.refresh_from_db()
    return response


def hemoglobin():
    return ConceptFactory(concept_code='718-7', vocabulary=VocabularyFactory(vocabulary_id='LOINC'))


def test_edit_appends_today_then_reuses_today_and_returns_current_value(editor):
    record, _ = editor
    concept = hemoglobin()
    yesterday = timezone.localdate() - timedelta(days=1)
    with suppress_patient_record_refresh():
        old = MeasurementFactory(person=record.person, measurement_concept=concept,
                                 measurement_source_value='718-7', measurement_date=yesterday,
                                 value_as_number=9)
    refresh_patient_record(record.person)
    response = patch_field(editor, 'hemoglobin_g_dl', 12)
    assert Decimal(str(response.data['hemoglobin_g_dl'])) == 12
    rows = Measurement.objects.filter(person=record.person, measurement_concept=concept)
    assert rows.count() == 2
    current = rows.get(measurement_date=timezone.localdate())
    assert current.value_as_number == 12
    assert current.unit_source_value == 'g/dL'
    patch_field(editor, 'hemoglobin_g_dl', 14)
    assert rows.count() == 2
    current.refresh_from_db()
    old.refresh_from_db()
    assert current.value_as_number == 14
    assert old.value_as_number == 9
    assert old.measurement_date == yesterday
    assert refresh_patient_record(record.person).hemoglobin_g_dl == 14


def test_same_day_import_is_updated_but_erroneous_and_other_concepts_are_not(editor):
    record, _ = editor
    concept = hemoglobin()
    with suppress_patient_record_refresh():
        same_day = MeasurementFactory(person=record.person, measurement_concept=concept,
                                      measurement_source_value='718-7', value_as_number=9,
                                      measurement_date=timezone.localdate())
        erroneous = MeasurementFactory(person=record.person, measurement_concept=concept,
                                       measurement_source_value='718-7', value_as_number=2,
                                       measurement_date=timezone.localdate(), is_erroneous=True)
        other = MeasurementFactory(person=record.person, measurement_source_value='718-7',
                                   value_as_number=3, measurement_date=timezone.localdate())
    patch_field(editor, 'hemoglobin_g_dl', 13)
    same_day.refresh_from_db()
    erroneous.refresh_from_db()
    other.refresh_from_db()
    assert same_day.value_as_number == 13
    assert erroneous.value_as_number == 2
    assert other.value_as_number == 3
    assert Measurement.objects.filter(person=record.person).count() == 3


def test_clear_is_durable_and_later_edit_uses_new_day(editor):
    record, _ = editor
    concept = hemoglobin()
    yesterday = timezone.localdate() - timedelta(days=1)
    with suppress_patient_record_refresh():
        old = MeasurementFactory(person=record.person, measurement_concept=concept,
                                 measurement_source_value='718-7', measurement_date=yesterday,
                                 value_as_number=9)
    refresh_patient_record(record.person)
    patch_field(editor, 'hemoglobin_g_dl', None)
    rows = Measurement.objects.filter(person=record.person, measurement_concept=concept)
    assert rows.count() == 2
    cleared = rows.get(measurement_date=timezone.localdate())
    assert cleared.value_source_value == CLEAR_VALUE
    assert cleared.value_as_number is None
    assert refresh_patient_record(record.person).hemoglobin_g_dl is None
    old.refresh_from_db()
    assert old.value_as_number == 9
    tomorrow = timezone.localdate() + timedelta(days=1)
    with patch('omop_core.services.omop_projection.timezone.localdate', return_value=tomorrow):
        patch_field(editor, 'hemoglobin_g_dl', 11)
    assert rows.count() == 3
    cleared.refresh_from_db()
    assert cleared.value_source_value == CLEAR_VALUE
    assert refresh_patient_record(record.person).hemoglobin_g_dl == 11


def test_clear_then_correct_same_day_reuses_row(editor):
    record, _ = editor
    concept = hemoglobin()
    patch_field(editor, 'hemoglobin_g_dl', 12)
    patch_field(editor, 'hemoglobin_g_dl', None)
    patch_field(editor, 'hemoglobin_g_dl', 13)
    row = Measurement.objects.get(person=record.person, measurement_concept=concept)
    assert row.value_source_value is None
    assert row.value_as_number == 13
    assert refresh_patient_record(record.person).hemoglobin_g_dl == 13


def test_wbc_uses_units_from_builtin_recipe(editor):
    record, _ = editor
    concept = ConceptFactory(concept_code='6690-2', vocabulary=VocabularyFactory(vocabulary_id='LOINC'))
    patch_field(editor, 'wbc_count_thousand_per_ul', 7)
    row = Measurement.objects.get(person=record.person, measurement_concept=concept)
    assert row.unit_source_value
    assert refresh_patient_record(record.person).wbc_count_thousand_per_ul == 7


def test_numeric_approval_backfills_only_pending_edits_with_units(editor):
    record, _ = editor
    concept = hemoglobin()
    unit = ConceptFactory(concept_code='g/dL', vocabulary=VocabularyFactory(vocabulary_id='UCUM'))
    record.hemoglobin_g_dl = 12
    record.user_edited_fields = ['hemoglobin_g_dl']
    record.save()
    untouched = PatientRecordFactory(hemoglobin_g_dl=10)
    mapping = FieldConceptMapping.objects.create(
        field_name='hemoglobin_g_dl', concept=concept, omop_table='measurement',
        source_value='718-7', unit='g/dL', value_kind='number', status='approved',
    )
    row = Measurement.objects.get(person=record.person, measurement_concept=concept)
    assert row.value_as_number == 12
    assert row.unit_source_value == 'g/dL'
    assert row.unit_concept_id == unit.pk
    assert not Measurement.objects.filter(person=untouched.person).exists()
    assert project_field_to_omop(mapping) == 0
    record.refresh_from_db()
    assert 'hemoglobin_g_dl' not in record.user_edited_fields


def test_projection_failure_keeps_edit_and_does_not_poison_transaction(editor):
    record, _ = editor
    concept = hemoglobin()
    with suppress_patient_record_refresh():
        MeasurementFactory(person=record.person, measurement_concept=concept,
                           measurement_source_value='718-7', value_as_number=9)
    refresh_patient_record(record.person)
    def fail_in_database(*args):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1 / 0')

    with patch('omop_core.services.omop_projection.next_pk', side_effect=fail_in_database):
        patch_field(editor, 'hemoglobin_g_dl', 14)
    assert record.hemoglobin_g_dl == 14
    assert 'hemoglobin_g_dl' in record.user_edited_fields
    assert refresh_patient_record(record.person).hemoglobin_g_dl == 14


def test_readonly_payload_cannot_project_and_echo_does_not_create_fact(editor):
    record, _ = editor
    hemoglobin()
    patch_field(editor, 'hemoglobin_g_dl', 12)
    patch_field(editor, 'hemoglobin_g_dl', 12)
    patch_field(editor, 'first_line_intent', 'not writable')
    assert Measurement.objects.filter(person=record.person).count() == 1
    assert record.first_line_intent is None
    assert 'first_line_intent' not in record.user_edited_fields
    assert not Observation.objects.filter(person=record.person).exists()


def test_patient_self_service_uses_same_omop_save_path(editor):
    from patient_portal.models import PatientUser
    record, _ = editor
    concept = hemoglobin()
    identity = Identity.objects.create_user(email='self-edit@example.test')
    PatientUser.objects.create(identity=identity, person=record.person)
    client = APIClient()
    client.force_authenticate(identity)
    for value in (12, 13):
        response = client.patch('/api/patient-info/me/', {'hemoglobin_g_dl': value}, format='json')
        assert response.status_code == 200, response.data
        assert Decimal(str(response.data['patient_info']['hemoglobin_g_dl'])) == value
    row = Measurement.objects.get(person=record.person, measurement_concept=concept)
    assert row.value_as_number == 13
    assert row.measurement_date == timezone.localdate()


@pytest.mark.parametrize('target', ['measurement', 'observation', 'condition', 'drug_exposure', 'procedure'])
def test_every_omop_target_preserves_earlier_days(editor, target):
    from omop_core.services.omop_projection import _TARGET_CONFIG, project_single_value
    record, _ = editor
    concept = ConceptFactory(concept_code='history-target')
    model, _, concept_field, date_field, _, source_field, _, _ = _TARGET_CONFIG[target]
    recipe = {'omop_table': target, 'concept_id': concept.pk,
              'source_value': 'history-target', 'type_concept_id': 32817}
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)
    with patch('omop_core.services.omop_projection.timezone.localdate', return_value=yesterday):
        assert project_single_value(record.person, 'test_field', 1, recipe)
    assert project_single_value(record.person, 'test_field', 2, recipe)
    project_single_value(record.person, 'test_field', 3, recipe)
    rows = model.objects.filter(person=record.person, **{concept_field: concept.pk, source_field: 'history-target'})
    assert rows.count() == 2
    old = rows.get(**{date_field: yesterday})
    current = rows.get(**{date_field: today})
    if target in ('measurement', 'observation'):
        assert old.value_as_number == 1
        assert current.value_as_number == 3


def test_date_mapping_approval_can_backfill_pending_dates(editor):
    record, _ = editor
    concept = ConceptFactory(concept_code='supportive-start')
    record.supportive_therapy_start_date = timezone.localdate() - timedelta(days=20)
    record.user_edited_fields = ['supportive_therapy_start_date']
    record.save()
    FieldConceptMapping.objects.create(
        field_name='supportive_therapy_start_date', concept=concept,
        omop_table='observation', source_value='supportive-start',
        value_kind='date', status='approved',
    )
    row = Observation.objects.get(person=record.person, observation_concept=concept)
    assert row.observation_date == timezone.localdate()
    assert row.value_as_string == record.supportive_therapy_start_date.isoformat()

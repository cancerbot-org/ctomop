import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from omop_core.models import SourceCodeConceptMapping
from patient_portal.api.views import code_mapping_accuracy
from patient_portal.models import Identity

pytestmark = pytest.mark.django_db


def test_icd10_accuracy_combines_aliases_for_latest_model():
    SourceCodeConceptMapping.objects.bulk_create([
        SourceCodeConceptMapping(
            source_vocabulary_id=vocab, source_code=code,
            suggestion_model_version=version, suggestion_outcome=outcome,
        )
        for vocab, code, version, outcome in [
            ('ICD10', 'A01', '0.2', 'accepted'),
            ('ICD10CM', 'A02', '0.2', 'rejected'),
            ('ICD10CM', 'A03', '0.2', 'overridden'),
            ('ICD10CM', 'A04', '0.1', 'accepted'),
        ]
    ])
    user = Identity.objects.create_user(email='accuracy-admin@example.test', is_staff=True)
    request = APIRequestFactory().get('/api/code-mappings/accuracy/')
    force_authenticate(request, user=user)

    response = code_mapping_accuracy(request)

    assert response.status_code == 200
    assert set(response.data['by_source_vocabulary']) == {'ICD10'}
    metrics = response.data['by_source_vocabulary']['ICD10']
    assert metrics['model_version'] == '0.2'
    assert metrics['suggestions'] == 3
    assert metrics['approved'] == 1
    assert metrics['rejected'] == 1
    assert metrics['overridden'] == 1
    assert metrics['precision'] == pytest.approx(1 / 3)
    assert metrics['recall'] == pytest.approx(1 / 2)
    assert metrics['f1'] == pytest.approx(0.4)


@pytest.mark.parametrize(('status', 'change_destination', 'outcome', 'counter'), [
    ('approved', False, 'accepted', 'approved'),
    ('rejected', False, 'rejected', 'rejected'),
    ('approved', True, 'overridden', 'overridden'),
])
def test_uncoded_reviews_of_older_models_are_counted(status, change_destination, outcome, counter):
    from rest_framework.test import APIClient
    from tests.factories import ConceptFactory, DomainFactory

    domain = DomainFactory(domain_id='Measurement')
    original = ConceptFactory(domain=domain, standard_concept='S')
    replacement = ConceptFactory(domain=domain, standard_concept='S')
    old = SourceCodeConceptMapping.objects.create(
        source_vocabulary_id='', source_code='Uncoded lab', domain_id='Measurement',
        omop_table='measurement', target_concept=original, suggested_target_concept=original,
        origin_system='suggest v0.1', suggestion_model_version='v0.1', status='proposed',
    )
    SourceCodeConceptMapping.objects.create(
        source_vocabulary_id='', source_code='New unreviewed lab',
        origin_system='suggest v0.2', suggestion_model_version='v0.2', status='proposed',
    )
    SourceCodeConceptMapping.objects.create(
        source_vocabulary_id='LOINC', source_code='external',
        suggestion_model_version='v0.2', suggestion_outcome='accepted',
    )
    client = APIClient()
    client.force_authenticate(Identity.objects.create_user(email='uncoded@example.test', is_staff=True))
    before = client.get('/api/v1/code-mappings/accuracy/').data
    assert before['by_source_vocabulary']['']['review_totals'] == dict(approved=0, rejected=0, overridden=0)
    response = client.patch(f'/api/v1/code-mappings/{old.pk}/', {
        'status': status,
        'destination_concept_id': replacement.pk if change_destination else original.pk,
    }, format='json')
    assert response.status_code == 200, response.data
    old.refresh_from_db()
    assert old.source_vocabulary_id == ''
    assert old.suggestion_outcome == outcome
    after = client.get('/api/v1/code-mappings/accuracy/').data
    uncoded = after['by_source_vocabulary']['']
    assert uncoded['review_totals'] == {key: int(key == counter) for key in ('approved', 'rejected', 'overridden')}
    # Keep the current model's precision/recall and historical model records
    # separate from the cumulative review counters.
    assert uncoded['model_version'] == 'v0.2'
    assert uncoded['reviewed'] == 0
    assert uncoded['precision'] is None
    assert after['overall']['review_totals']['approved'] == 1 + int(counter == 'approved')
    history = client.get('/api/v1/code-mappings/accuracy/dashboard/').data['models']
    assert next(model for model in history if model['model_version'] == 'v0.1')[counter] == 1


def test_accuracy_uses_one_query_for_all_vocabularies():
    from django.db import connection
    from django.test.utils import CaptureQueriesContext
    for source in ['', 'ICD10', 'ICD10CM', 'LOINC', 'SNOMED', 'Apple', 'Garmin']:
        SourceCodeConceptMapping.objects.create(
            source_vocabulary_id=source, source_code='one',
            suggestion_model_version='v0.2', suggestion_outcome='rejected',
        )
    request = APIRequestFactory().get('/api/v1/code-mappings/accuracy/')
    force_authenticate(request, user=Identity.objects.create_user(email='query-count@example.test', is_staff=True))
    with CaptureQueriesContext(connection) as queries:
        response = code_mapping_accuracy(request)
    assert len(queries) == 1
    assert response.data['overall']['review_totals']['rejected'] == 7
    assert response.data['by_source_vocabulary']['']['review_totals']['rejected'] == 1
    assert response.data['by_source_vocabulary']['ICD10']['review_totals']['rejected'] == 2
    assert response.data['by_source_vocabulary']['OpenWearables']['review_totals']['rejected'] == 2

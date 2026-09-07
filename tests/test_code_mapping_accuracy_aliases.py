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

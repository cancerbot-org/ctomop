import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from omop_core.models import SourceCodeConceptMapping
from patient_portal.api.views import code_mapping_list
from patient_portal.models import Identity

pytestmark = pytest.mark.django_db


@pytest.fixture
def browse():
    user = Identity.objects.create_user(email='browse@example.test', is_staff=True)

    def get(**params):
        request = APIRequestFactory().get('/api/v1/code-mappings/', {'browse': '1', **params})
        force_authenticate(request, user=user)
        return code_mapping_list(request)
    return get


def row(code, **kwargs):
    return SourceCodeConceptMapping.objects.create(source_code=code, **{'source_vocabulary_id': 'ICD10', 'status': 'proposed', **kwargs})


def test_pages_sort_before_slicing_and_report_full_counts(browse):
    for i in range(105):
        row(f'C{i:03}', occurrence_count=i)
    first = browse().data
    assert len(first['results']) == 50
    assert first['results'][0]['source_code'] == 'C104'
    assert first['pages']['Unmapped'] == {'page': 1, 'page_size': 50, 'total': 105}
    assert first['tabs'][0]['proposed'] == 105
    second = browse(page_0=2).data
    assert second['results'][0]['source_code'] == 'C054'
    assert {r['mapping_id'] for r in first['results']}.isdisjoint(r['mapping_id'] for r in second['results'])
    assert browse(page_0=99).data['pages']['Unmapped']['page'] == 3
    assert browse(order_0='source_code').data['results'][0]['source_code'] == 'C000'


def test_aliases_global_search_rejected_and_sections(browse):
    row('A', source_vocabulary_id='ICD10CM', occurrence_count=50)
    row('B', status='approved')
    row('C', status='rejected')
    row('D', source_vocabulary_id='LOINC', source_code_description='distinctive phrase')
    row('E', origin_system='athena', status='approved')
    data = browse(source='ICD10').data
    assert {r['source_code'] for r in data['results']} == {'A', 'B', 'E'}
    assert data['rejected_count'] == 1
    assert len(browse(source='ICD10', show_rejected='true').data['results']) == 4
    assert [r['source_code'] for r in browse(source='ICD10', search='distinctive').data['results']] == ['D']
    assert browse(source='').data['results'] == []


def test_duplicates_include_off_page_and_rejected_members(browse):
    row('MATCH', occurrence_count=0)
    row(' match ', source_vocabulary_id='ICD10CM', status='rejected')
    for i in range(51):
        row(f'X{i}', occurrence_count=100)
    data = browse(search='X').data
    assert {r['source_code'] for r in data['duplicates']} == {'MATCH', ' match '}
    assert len(data['results']) == 50


def test_bad_paging_or_sort_is_a_validation_error(browse):
    assert browse(page_0='bad').status_code == 400
    assert browse(order_0='password').status_code == 400

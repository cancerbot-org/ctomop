"""An approved concept mapping is what makes a field writable.

The curation interface records a decision per PatientRecord field. Until now
nothing acted on it: `FieldConceptMapping` said in its own docstring that it
"does NOT make the field writable", so a curator could approve a mapping, see it
listed as approved, and find the field exactly as read-only as before.

These pin the other half — the descriptor reads approved mappings and emits an
editable entry — and the bar a row has to clear before it counts. A concept says
what a fact means; it does not say where the fact goes or how to find it again.
"""
import pytest

from omop_core.models import FieldConceptMapping
from omop_core.services.write_descriptor import build_writable_field_descriptor
from tests.factories import ConceptFactory, VocabularyFactory

pytestmark = pytest.mark.django_db

FIELD = 'planned_therapies'   # unmapped by default, so a clean subject


def _concept():
    VocabularyFactory(vocabulary_id='SNOMED')
    return ConceptFactory(
        concept_code='313059006', vocabulary_id='SNOMED',
        concept_name='Planned therapy',
    )


def _mapping(**overrides):
    defaults = {
        'field_name': FIELD,
        'concept': _concept(),
        'omop_table': 'observation',
        'source_value': 'planned-therapies',
        'value_kind': 'string',
        'status': 'approved',
    }
    defaults.update(overrides)
    return FieldConceptMapping.objects.create(**defaults)


class TestAnApprovedMappingMakesTheFieldWritable:
    def test_the_field_becomes_editable(self):
        mapping = _mapping()

        entry = build_writable_field_descriptor()[FIELD]

        assert entry['kind'] == 'editable'
        assert entry['writable'] is True
        assert entry['target'] == 'observation'
        assert entry['concept_id'] == mapping.concept_id
        assert entry['source_value'] == 'planned-therapies'

    def test_it_carries_everything_a_write_needs(self):
        _mapping()

        entry = build_writable_field_descriptor()[FIELD]

        required = {'target', 'concept_id', 'value_kind', 'type_concept_id',
                    'source_value'}
        assert required <= set(entry)

    def test_it_is_marked_as_curated(self):
        # Distinguishes a field made writable by a reviewer from one hardcoded
        # in the mapping tables, which matters when explaining where a write
        # path came from.
        _mapping()
        assert build_writable_field_descriptor()[FIELD]['curated'] is True


class TestAnIncompleteMappingIsStillAdvisory:
    """Short of a full recipe, a mapping records a decision and nothing more.

    Offering a box that writes a row derivation cannot find is worse than
    offering none: the save succeeds and the value never comes back.
    """

    def test_a_proposed_mapping_does_not_count(self):
        _mapping(status='proposed')
        assert build_writable_field_descriptor()[FIELD]['writable'] is False

    def test_a_rejected_mapping_does_not_count(self):
        _mapping(status='rejected')
        assert build_writable_field_descriptor()[FIELD]['writable'] is False

    def test_a_mapping_without_a_source_value_does_not_count(self):
        # Derivation matches on source_value. Without one the written row is
        # unfindable, so the field would appear to save and never change.
        _mapping(source_value='')
        assert build_writable_field_descriptor()[FIELD]['writable'] is False

    def test_a_mapping_without_a_concept_does_not_count(self):
        _mapping(concept=None)
        assert build_writable_field_descriptor()[FIELD]['writable'] is False

    def test_a_mapping_to_a_table_this_cannot_write_does_not_count(self):
        _mapping(omop_table='visit_occurrence')
        assert build_writable_field_descriptor()[FIELD]['writable'] is False

    @pytest.mark.parametrize(('omop_table', 'target'), [
        ('measurement', 'measurement'),
        ('observation', 'observation'),
        ('condition_occurrence', 'condition'),
        ('condition', 'condition'),
        ('drug_exposure', 'drug_exposure'),
        ('drug', 'drug_exposure'),
        ('procedure_occurrence', 'procedure'),
        ('procedure', 'procedure'),
    ])
    def test_supported_omop_tables_make_curated_fields_writable(self, omop_table, target):
        _mapping(omop_table=omop_table)

        entry = build_writable_field_descriptor()[FIELD]

        assert entry['writable'] is True
        assert entry['target'] == target
        assert entry['endpoint'].startswith('POST /api/v1/')


@pytest.mark.parametrize('omop_table,source_column', [
    ('measurement', 'measurement.measurement_source_value'),
    ('observation', 'observation.observation_source_value'),
    ('condition', 'condition_occurrence.condition_source_value'),
    ('condition_occurrence', 'condition_occurrence.condition_source_value'),
    ('drug', 'drug_exposure.drug_source_value'),
    ('drug_exposure', 'drug_exposure.drug_source_value'),
    ('procedure', 'procedure_occurrence.procedure_source_value'),
    ('procedure_occurrence', 'procedure_occurrence.procedure_source_value'),
])
@pytest.mark.parametrize('length', [50, 51, 100])
def test_curated_source_value_must_fit_target_column(omop_table, source_column, length):
    # Non-ASCII characters count as characters, not UTF-8 bytes, in PostgreSQL.
    source_value = 'é' * length
    mapping = _mapping(omop_table=omop_table, source_value=source_value)

    entry = build_writable_field_descriptor()[FIELD]

    assert entry['curated'] is True
    assert entry['writable'] is (length <= 50)
    if length <= 50:
        assert entry['source_value'] == source_value
    else:
        assert '50-character' in entry['reason']
        assert source_column in entry['reason']
    mapping.refresh_from_db()
    assert mapping.source_value == source_value


def test_overlong_curated_mapping_blocks_fallback_recipe():
    VocabularyFactory(vocabulary_id='LOINC')
    ConceptFactory(concept_code='718-7', vocabulary_id='LOINC')
    assert build_writable_field_descriptor()['hemoglobin_g_dl']['writable'] is True
    _mapping(field_name='hemoglobin_g_dl', source_value='x' * 51)

    entry = build_writable_field_descriptor()['hemoglobin_g_dl']

    assert entry['writable'] is False
    assert entry['curated'] is True
    assert 'source_value exceeds' in entry['reason']


class TestBoundedAnswers:
    def test_a_value_vocabulary_becomes_the_offered_options(self):
        # The vocabulary tables are seeded by their own migrations; this reads
        # whatever is there rather than inventing rows, because ingest filters
        # against exactly the same set.
        from omop_core.models import SctEligibility

        expected = list(
            SctEligibility.objects.order_by('title').values_list('title', flat=True)
        )
        assert expected, 'expected the SctEligibility vocabulary to be seeded'
        _mapping(value_vocabulary='SctEligibility', multiple=True)

        entry = build_writable_field_descriptor()[FIELD]

        assert [o['value'] for o in entry['options']] == expected
        assert entry['multiple'] is True

    def test_an_unknown_vocabulary_name_is_ignored_not_fatal(self):
        # A curator can mistype. The field stays writable as free text rather
        # than the whole descriptor failing to build.
        _mapping(value_vocabulary='NoSuchVocabulary')

        entry = build_writable_field_descriptor()[FIELD]

        assert entry['writable'] is True
        assert 'options' not in entry

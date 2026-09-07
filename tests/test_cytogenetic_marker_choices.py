"""Regression coverage for the cytogenetic marker value set (#1047)."""

import pytest

from omop_core.models import FieldChoice, FieldChoiceCode, PatientRecord
from omop_core.services.mappings import SUGGESTED_FIELD_CODES


@pytest.mark.django_db
def test_cytogenetic_marker_field_is_correctly_named_and_coded():
    """The field and the choices use the same canonical codes as FHIR ingest."""
    assert PatientRecord._meta.get_field('cytogenetic_markers')
    assert 'cytogenic_markers' not in {
        field.name for field in PatientRecord._meta.get_fields()
    }
    assert SUGGESTED_FIELD_CODES['cytogenetic_markers'] == ('69548-6', 'LOINC')

    choices = {
        choice.display: choice
        for choice in FieldChoice.objects.filter(field_name='cytogenetic_markers')
    }
    assert {'del17p', 't(4;14)', 't(11;14)', '1q_amp', 'hyperdiploidy',
            'MYC rearrangement'} <= choices.keys()

    codes = {
        row.choice.display: row.code
        for row in FieldChoiceCode.objects.filter(choice__in=choices.values(), is_primary=True)
    }
    assert codes['del17p'] == '72838-3'
    assert codes['t(4;14)'] == '72842-5'
    assert codes['1q_amp'] == '81249-5'
    assert codes['hyperdiploidy'] == '81248-7'
    # These are selectable now; a reviewed standard code may be added later.
    assert 't(11;14)' not in codes
    assert 'MYC rearrangement' not in codes

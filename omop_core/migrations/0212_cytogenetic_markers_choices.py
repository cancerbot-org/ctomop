"""Correct the cytogenetic field name and seed its standard coded values."""

import logging

from django.db import migrations


logger = logging.getLogger(__name__)

LEGACY_FIELD = 'cytogenic_markers'
FIELD = 'cytogenetic_markers'

# The same canonical values and LOINC result codes emitted by the myeloma FHIR
# generator.  They let a chooser, an imported Observation and a matcher speak
# the same vocabulary without putting the non-standard MeSH heading in a
# standard OMOP concept column.  MYC and t(11;14) remain selectable but uncoded
# until a reviewed standard concept is selected for them.
CHOICES = (
    ('del17p', '72838-3', 'TP53/17p deletion'),
    ('t(4;14)', '72842-5', 'FGFR3/IGH translocation t(4;14)'),
    ('t(11;14)', None, ''),
    ('t(14;16)', '81250-3', 'MAF/IGH translocation t(14;16)'),
    ('1q_gain', '81249-5', '1q21 gain/amplification'),
    ('1q_amp', '81249-5', '1q21 amplification (4 or more copies)'),
    ('hyperdiploidy', '81248-7', 'Hyperdiploidy'),
    ('del13q', '72840-9', '13q deletion'),
    ('MYC rearrangement', None, ''),
)


def migrate_and_seed(apps, schema_editor):
    FieldChoice = apps.get_model('omop_core', 'FieldChoice')
    FieldChoiceCode = apps.get_model('omop_core', 'FieldChoiceCode')
    FieldConceptMapping = apps.get_model('omop_core', 'FieldConceptMapping')
    FieldFormula = apps.get_model('omop_core', 'FieldFormula')
    FieldSynonym = apps.get_model('omop_core', 'FieldSynonym')
    Concept = apps.get_model('omop_core', 'Concept')

    # These tables use a string field name rather than a foreign key, so a
    # RenameField alone cannot preserve curator-managed metadata.
    for model in (FieldChoice, FieldFormula, FieldSynonym):
        model.objects.filter(field_name=LEGACY_FIELD).update(field_name=FIELD)

    legacy_mapping = FieldConceptMapping.objects.filter(
        field_name=LEGACY_FIELD, vocabulary_id='MeSH', concept_code='D002869')
    legacy_mapping.delete()
    FieldConceptMapping.objects.filter(field_name=LEGACY_FIELD).update(field_name=FIELD)

    question = Concept.objects.filter(
        vocabulary_id='LOINC', concept_code='69548-6').first()
    if question is None:
        logger.warning('LOINC:69548-6 missing; no proposed cytogenetic mapping seeded.')
    else:
        FieldConceptMapping.objects.get_or_create(
            field_name=FIELD,
            defaults={
                'concept': question,
                'vocabulary_id': 'LOINC',
                'concept_code': '69548-6',
                'status': 'proposed',
                'notes': 'Cytogenomic microarray result question (#1047).',
            },
        )

    for sort_order, (display, code, code_display) in enumerate(CHOICES):
        choice, _ = FieldChoice.objects.get_or_create(
            field_name=FIELD, display=display,
            defaults={'sort_order': sort_order},
        )
        if code:
            FieldChoiceCode.objects.update_or_create(
                choice=choice, vocabulary_id='LOINC', code=code,
                defaults={'display': code_display, 'is_primary': True},
            )


class Migration(migrations.Migration):

    dependencies = [('omop_core', '0211_backfill_versioned_suggestion_targets')]

    operations = [
        migrations.RenameField(
            model_name='patientrecord',
            old_name=LEGACY_FIELD,
            new_name=FIELD,
        ),
        migrations.RunPython(migrate_and_seed, migrations.RunPython.noop),
    ]

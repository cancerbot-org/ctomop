from django.db import migrations


def enable_authoring(apps, schema_editor):
    Concept = apps.get_model('omop_core', 'Concept')
    Mapping = apps.get_model('omop_core', 'FieldConceptMapping')
    concept = Concept.objects.filter(vocabulary_id='LOINC', concept_code='69548-6').first()
    if concept is None:
        return
    Mapping.objects.update_or_create(
        field_name='cytogenetic_markers',
        defaults={
            'concept': concept, 'vocabulary_id': 'LOINC', 'concept_code': '69548-6',
            'omop_table': 'observation', 'source_value': 'mm-cytogenetic-markers',
            'value_kind': 'string', 'multiple': True, 'status': 'approved',
            'notes': 'Approved UI authoring recipe for cytogenetic marker values (#1050).',
        },
    )


class Migration(migrations.Migration):
    dependencies = [('omop_core', '0212_cytogenetic_markers_choices')]
    operations = [migrations.RunPython(enable_authoring, migrations.RunPython.noop)]

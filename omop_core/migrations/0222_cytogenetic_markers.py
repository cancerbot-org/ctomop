"""Rename and enable the PatientRecord-first cytogenetic marker field."""

import logging

from django.db import migrations


logger = logging.getLogger(__name__)
LEGACY_FIELD = 'cytogenic_markers'
FIELD = 'cytogenetic_markers'

# (stored/display value, LOINC result code, code display)
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

    for model in (FieldChoice, FieldFormula, FieldSynonym):
        model.objects.filter(field_name=LEGACY_FIELD).update(field_name=FIELD)

    FieldConceptMapping.objects.filter(
        field_name=LEGACY_FIELD,
        vocabulary_id='MeSH',
        concept_code='D002869',
    ).delete()
    FieldConceptMapping.objects.filter(field_name=LEGACY_FIELD).update(field_name=FIELD)

    for sort_order, (display, code, code_display) in enumerate(CHOICES):
        choice, _ = FieldChoice.objects.get_or_create(
            field_name=FIELD,
            display=display,
            defaults={'sort_order': sort_order},
        )
        if code:
            FieldChoiceCode.objects.update_or_create(
                choice=choice,
                vocabulary_id='LOINC',
                code=code,
                defaults={'display': code_display, 'is_primary': True},
            )

    question = Concept.objects.filter(
        vocabulary_id='LOINC', concept_code='69548-6', invalid_reason__isnull=True,
    ).first()
    mapping_defaults = {
        'concept': question,
        'vocabulary_id': 'LOINC',
        'concept_code': '69548-6',
        'omop_table': 'observation',
        'source_value': 'mm-cytogenetic-markers',
        'value_kind': 'string',
        'multiple': True,
        'status': 'approved' if question else 'proposed',
        'notes': (
            'PatientRecord-first projection for a canonical comma-separated '
            'cytogenetic marker list (#1047/#1050/#1051).'
        ),
    }
    FieldConceptMapping.objects.update_or_create(
        field_name=FIELD, defaults=mapping_defaults,
    )
    if question is None:
        logger.warning(
            'LOINC:69548-6 missing; cytogenetic markers remain direct-only '
            'until the mapping is resolved and approved.'
        )


def reverse_metadata(apps, schema_editor):
    for model_name in ('FieldChoice', 'FieldFormula', 'FieldSynonym', 'FieldConceptMapping'):
        model = apps.get_model('omop_core', model_name)
        model.objects.filter(field_name=FIELD).update(field_name=LEGACY_FIELD)


def _rebuild_view(old_output, new_output, table_column):
    return f"""
DO $$
DECLARE
    col_list text;
    view_acl aclitem[];
    view_owner text;
    stmt text;
BEGIN
    IF to_regclass('public.patient_info') IS NULL THEN
        RETURN;
    END IF;

    SELECT string_agg(
               CASE
                   WHEN v.attname = '{old_output}'
                       THEN format('%I AS %I', '{table_column}', '{new_output}')
                   WHEN EXISTS (
                       SELECT 1 FROM pg_attribute t
                        WHERE t.attrelid = to_regclass('public.patient_record')
                          AND t.attname = v.attname
                          AND t.attnum > 0 AND NOT t.attisdropped
                   ) THEN quote_ident(v.attname)
                   ELSE format('NULL::%s AS %I',
                               format_type(v.atttypid, v.atttypmod), v.attname)
               END,
               ', ' ORDER BY v.attnum)
      INTO col_list
      FROM pg_attribute v
     WHERE v.attrelid = to_regclass('public.patient_info')
       AND v.attnum > 0 AND NOT v.attisdropped;

    SELECT c.relacl, pg_get_userbyid(c.relowner)
      INTO view_acl, view_owner
      FROM pg_class c WHERE c.oid = to_regclass('public.patient_info');

    EXECUTE 'DROP VIEW public.patient_info';
    EXECUTE format(
        'CREATE VIEW public.patient_info AS SELECT %s FROM public.patient_record',
        col_list);
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'patient_info_readonly') THEN
        EXECUTE 'CREATE TRIGGER patient_info_readonly_trigger '
                'INSTEAD OF INSERT OR UPDATE OR DELETE ON public.patient_info '
                'FOR EACH ROW EXECUTE FUNCTION patient_info_readonly()';
    END IF;

    BEGIN
        IF view_owner IS NOT NULL AND view_owner <> current_user THEN
            EXECUTE format('ALTER VIEW public.patient_info OWNER TO %I', view_owner);
        END IF;
    EXCEPTION WHEN OTHERS THEN
        RAISE WARNING 'patient_info: could not restore owner %: %', view_owner, SQLERRM;
    END;

    IF view_acl IS NOT NULL THEN
        FOR stmt IN
            SELECT format('GRANT %s ON public.patient_info TO %s%s',
                          a.privilege_type,
                          CASE WHEN a.grantee = 0 THEN 'PUBLIC'
                               ELSE quote_ident(pg_get_userbyid(a.grantee)) END,
                          CASE WHEN a.is_grantable THEN ' WITH GRANT OPTION' ELSE '' END)
              FROM aclexplode(view_acl) a
        LOOP
            BEGIN
                EXECUTE stmt;
            EXCEPTION WHEN OTHERS THEN
                RAISE WARNING 'patient_info: could not restore grant (%): %', stmt, SQLERRM;
            END;
        END LOOP;
    END IF;
END
$$;
"""


FORWARD_VIEW_SQL = _rebuild_view(LEGACY_FIELD, FIELD, FIELD)
# Reverse SQL runs before Django reverses RenameField, so the table column is
# still correctly spelled while the compatibility view is changed back.
REVERSE_VIEW_SQL = _rebuild_view(FIELD, LEGACY_FIELD, FIELD)


class Migration(migrations.Migration):
    dependencies = [('omop_core', '0221_seed_treatment_editor_catalogs')]

    operations = [
        migrations.RenameField(
            model_name='patientrecord', old_name=LEGACY_FIELD, new_name=FIELD,
        ),
        migrations.RunPython(migrate_and_seed, reverse_metadata),
        migrations.RunSQL(sql=FORWARD_VIEW_SQL, reverse_sql=REVERSE_VIEW_SQL),
    ]

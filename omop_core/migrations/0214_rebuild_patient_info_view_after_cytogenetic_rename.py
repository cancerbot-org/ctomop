from django.db import migrations


# ``patient_info`` is a PostgreSQL compatibility view whose SELECT list was
# frozen when it was created.  Renaming the underlying PatientRecord field in
# 0212 leaves the old ``cytogenic_markers`` view column behind: it no longer
# has a backing table column and breaks the compatibility-view contract.
# Rebuild from the existing view list, retaining backed columns plus the
# deliberate typed-NULL ``status`` compatibility column.  This deliberately
# does not widen the public view by adding new model columns (0151 behaviour).
REBUILD_VIEW_SQL = """
DO $$
DECLARE
    col_list text;
    view_acl aclitem[];
    view_owner text;
    stmt text;
BEGIN
    IF to_regclass('public.patient_info') IS NULL THEN
        RAISE NOTICE 'patient_info view not found; nothing to rebuild';
        RETURN;
    END IF;

    SELECT string_agg(
               CASE WHEN EXISTS (
                        SELECT 1
                          FROM pg_attribute t
                         WHERE t.attrelid = to_regclass('public.patient_record')
                           AND t.attname = v.attname
                           AND t.attnum > 0
                           AND NOT t.attisdropped
                    ) THEN quote_ident(v.attname)
                    ELSE format('NULL::%s AS %I',
                                format_type(v.atttypid, v.atttypmod), v.attname)
               END,
               ', ' ORDER BY v.attnum)
      INTO col_list
      FROM pg_attribute v
     WHERE v.attrelid = to_regclass('public.patient_info')
       AND v.attnum > 0
       AND NOT v.attisdropped
       -- status is deliberately retained as a typed NULL (0138); this is the
       -- one genuinely stale column introduced by the 0212 rename.
       AND v.attname <> 'cytogenic_markers';

    SELECT c.relacl, pg_get_userbyid(c.relowner)
      INTO view_acl, view_owner
      FROM pg_class c
     WHERE c.oid = to_regclass('public.patient_info');

    EXECUTE 'DROP VIEW public.patient_info';
    EXECUTE format(
        'CREATE VIEW public.patient_info AS SELECT %s FROM public.patient_record',
        col_list);
    EXECUTE '
        CREATE TRIGGER patient_info_readonly_trigger
        INSTEAD OF INSERT OR UPDATE OR DELETE ON public.patient_info
        FOR EACH ROW EXECUTE FUNCTION patient_info_readonly()';

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


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0213_enable_cytogenetic_marker_authoring'),
    ]

    operations = [
        migrations.RunSQL(sql=REBUILD_VIEW_SQL, reverse_sql=REBUILD_VIEW_SQL),
    ]

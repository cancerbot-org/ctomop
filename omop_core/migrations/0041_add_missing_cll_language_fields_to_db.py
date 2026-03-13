# Migration to add columns that are in Django model state (migration 0036 registered them)
# but were never actually created in the database (0036's SQL partially failed).
# Uses SeparateDatabaseAndState: only runs SQL, no state changes needed.

from django.db import migrations

ADD_SQL = """
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS absolute_lymphocyte_count DOUBLE PRECISION;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS autoimmune_cytopenias_refractory_to_steroids BOOLEAN;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS bcl2_inhibitor_refractory BOOLEAN;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS binet_stage TEXT;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS bone_marrow_involvement BOOLEAN;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS btk_inhibitor_refractory BOOLEAN;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS clonal_b_lymphocyte_count INTEGER;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS clonal_bone_marrow_b_lymphocytes DOUBLE PRECISION;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS disease_activity TEXT;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS flipi_score INTEGER;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS flipi_score_options TEXT;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS gelf_criteria_status TEXT;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS hepatomegaly BOOLEAN;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS languages_skills TEXT;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS largest_lymph_node_size DOUBLE PRECISION;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS later_therapies JSONB DEFAULT '[]'::jsonb;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS lymphadenopathy BOOLEAN;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS lymphocyte_doubling_time INTEGER;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS measurable_disease_imwg BOOLEAN;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS measurable_disease_iwcll BOOLEAN;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS protein_expressions TEXT;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS qtcf_value DOUBLE PRECISION;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS richter_transformation TEXT;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS serum_beta2_microglobulin_level DOUBLE PRECISION;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS spleen_size DOUBLE PRECISION;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS splenomegaly BOOLEAN;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS tp53_disruption BOOLEAN;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS tumor_burden TEXT;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS tumor_grade INTEGER;
"""

DROP_SQL = """
    ALTER TABLE patient_info DROP COLUMN IF EXISTS tumor_grade;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS tumor_burden;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS tp53_disruption;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS splenomegaly;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS spleen_size;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS serum_beta2_microglobulin_level;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS richter_transformation;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS qtcf_value;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS protein_expressions;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS measurable_disease_iwcll;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS measurable_disease_imwg;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS lymphocyte_doubling_time;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS lymphadenopathy;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS later_therapies;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS largest_lymph_node_size;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS languages_skills;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS hepatomegaly;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS gelf_criteria_status;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS flipi_score_options;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS flipi_score;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS disease_activity;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS clonal_bone_marrow_b_lymphocytes;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS clonal_b_lymphocyte_count;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS btk_inhibitor_refractory;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS bone_marrow_involvement;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS binet_stage;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS bcl2_inhibitor_refractory;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS autoimmune_cytopenias_refractory_to_steroids;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS absolute_lymphocyte_count;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0040_remove_status_field'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(sql=ADD_SQL, reverse_sql=DROP_SQL),
            ],
            state_operations=[],  # All fields already registered in Django state by migration 0036
        ),
    ]

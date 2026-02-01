# Migration for cancer assessment, treatment, and lab fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0031_make_condition_fields_nullable'),
    ]

    operations = [
        # Add new fields using raw SQL with IF NOT EXISTS
        migrations.RunSQL(
            sql="""
                -- Cancer Assessment Fields
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS ecog_assessment_date DATE;
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS test_methodology VARCHAR(50);
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS test_date DATE;
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS test_specimen_type VARCHAR(50);
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS report_interpretation VARCHAR(50);
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS oncotype_dx_score INTEGER;
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS ki67_percentage NUMERIC(5, 1);
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS androgen_receptor_status VARCHAR(50);
                
                -- Treatment Fields
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS therapy_intent VARCHAR(50);
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS reason_for_discontinuation VARCHAR(100);
                
                -- Additional Lab Values
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS ldh INTEGER;
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS alkaline_phosphatase INTEGER;
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS magnesium NUMERIC(5, 1);
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS phosphorus NUMERIC(5, 1);
                
                -- Reproductive Health
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS pregnancy_test_date DATE;
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS pregnancy_test_result_value VARCHAR(50);
            """,
            reverse_sql="""
                ALTER TABLE patient_info DROP COLUMN IF EXISTS pregnancy_test_result_value;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS pregnancy_test_date;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS phosphorus;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS magnesium;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS alkaline_phosphatase;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS ldh;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS reason_for_discontinuation;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS therapy_intent;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS androgen_receptor_status;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS ki67_percentage;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS oncotype_dx_score;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS report_interpretation;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS test_specimen_type;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS test_date;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS test_methodology;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS ecog_assessment_date;
            """
        ),
    ]

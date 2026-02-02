# Generated manually 2026-02-02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("omop_core", "0032_add_cancer_assessment_and_lab_fields"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS first_line_start_date DATE;
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS first_line_end_date DATE;
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS first_line_intent VARCHAR(50);
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS first_line_discontinuation_reason VARCHAR(50);
                
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS second_line_start_date DATE;
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS second_line_end_date DATE;
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS second_line_intent VARCHAR(50);
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS second_line_discontinuation_reason VARCHAR(50);
                
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS later_start_date DATE;
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS later_end_date DATE;
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS later_intent VARCHAR(50);
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS later_discontinuation_reason VARCHAR(50);
            """,
            reverse_sql="""
                ALTER TABLE patient_info DROP COLUMN IF EXISTS later_discontinuation_reason;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS later_intent;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS later_end_date;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS later_start_date;
                
                ALTER TABLE patient_info DROP COLUMN IF EXISTS second_line_discontinuation_reason;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS second_line_intent;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS second_line_end_date;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS second_line_start_date;
                
                ALTER TABLE patient_info DROP COLUMN IF EXISTS first_line_discontinuation_reason;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS first_line_intent;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS first_line_end_date;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS first_line_start_date;
            """,
        ),
    ]

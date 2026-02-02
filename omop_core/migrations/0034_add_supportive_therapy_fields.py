# Generated manually 2026-02-02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("omop_core", "0033_add_therapy_dates_and_intent"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS supportive_therapy_start_date DATE;
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS supportive_therapy_end_date DATE;
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS supportive_therapy_intent VARCHAR(50);
            """,
            reverse_sql="""
                ALTER TABLE patient_info DROP COLUMN IF EXISTS supportive_therapy_intent;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS supportive_therapy_end_date;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS supportive_therapy_start_date;
            """,
        ),
    ]

# Generated manually 2026-02-02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("omop_core", "0034_add_supportive_therapy_fields"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS planned_therapies TEXT;
            """,
            reverse_sql="""
                ALTER TABLE patient_info DROP COLUMN IF EXISTS planned_therapies;
            """,
        ),
    ]

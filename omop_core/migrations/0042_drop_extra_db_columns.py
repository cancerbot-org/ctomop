# Drop columns that exist in the DB but were removed from the Django model in migration 0037.
# Django's migration state already has these removed; this only performs the actual DB DROP.

from django.db import migrations

DROP_SQL = """
    ALTER TABLE patient_info DROP COLUMN IF EXISTS ai_lines_of_therapy;
    ALTER TABLE patient_info DROP COLUMN IF EXISTS survey_responses;
"""

RESTORE_SQL = """
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS ai_lines_of_therapy TEXT;
    ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS survey_responses JSONB;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0041_add_missing_cll_language_fields_to_db'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(sql=DROP_SQL, reverse_sql=RESTORE_SQL),
            ],
            state_operations=[],  # Already removed from state in migration 0037
        ),
    ]

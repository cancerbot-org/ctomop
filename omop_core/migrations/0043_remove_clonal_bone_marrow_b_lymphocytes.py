from django.db import migrations

DROP_SQL = "ALTER TABLE patient_info DROP COLUMN IF EXISTS clonal_bone_marrow_b_lymphocytes;"
ADD_SQL = "ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS clonal_bone_marrow_b_lymphocytes FLOAT;"


class Migration(migrations.Migration):
    dependencies = [("omop_core", "0042_drop_extra_db_columns")]
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunSQL(sql=DROP_SQL, reverse_sql=ADD_SQL)],
            state_operations=[
                migrations.RemoveField(
                    model_name="patientinfo",
                    name="clonal_bone_marrow_b_lymphocytes",
                )
            ],
        )
    ]

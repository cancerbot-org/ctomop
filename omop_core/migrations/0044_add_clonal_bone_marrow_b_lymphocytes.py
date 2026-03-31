from django.db import migrations, models

ADD_SQL = "ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS clonal_bone_marrow_b_lymphocytes FLOAT;"
DROP_SQL = "ALTER TABLE patient_info DROP COLUMN IF EXISTS clonal_bone_marrow_b_lymphocytes;"


class Migration(migrations.Migration):
    dependencies = [("omop_core", "0043_remove_clonal_bone_marrow_b_lymphocytes")]
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunSQL(sql=ADD_SQL, reverse_sql=DROP_SQL)],
            state_operations=[
                migrations.AddField(
                    model_name="patientinfo",
                    name="clonal_bone_marrow_b_lymphocytes",
                    field=models.FloatField(blank=True, null=True, help_text="Clonal B lymphocytes in bone marrow biopsy (%)"),
                )
            ],
        )
    ]

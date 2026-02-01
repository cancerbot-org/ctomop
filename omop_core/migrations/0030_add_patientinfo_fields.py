# Migration for additional PatientInfo fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0029_add_measurement_columns'),
    ]

    operations = [
        # Add patient_info fields using raw SQL with IF NOT EXISTS
        migrations.RunSQL(
            sql="""
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS city VARCHAR(255);
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS date_of_birth DATE;
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
                ALTER TABLE patient_info ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            """,
            reverse_sql="""
                ALTER TABLE patient_info DROP COLUMN IF EXISTS updated_at;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS created_at;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS date_of_birth;
                ALTER TABLE patient_info DROP COLUMN IF EXISTS city;
            """
        ),
    ]

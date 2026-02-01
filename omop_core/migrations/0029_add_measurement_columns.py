# Migration for OMOP CDM measurement table additions

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0028_add_behavior_fields'),
    ]

    operations = [
        # Add missing OMOP CDM measurement columns using raw SQL with IF NOT EXISTS
        migrations.RunSQL(
            sql="""
                ALTER TABLE measurement ADD COLUMN IF NOT EXISTS measurement_date DATE;
                ALTER TABLE measurement ADD COLUMN IF NOT EXISTS measurement_time VARCHAR(10);
                ALTER TABLE measurement ADD COLUMN IF NOT EXISTS value_as_string VARCHAR(60);
                ALTER TABLE measurement ADD COLUMN IF NOT EXISTS qualifier_concept_id INTEGER;
                ALTER TABLE measurement ADD COLUMN IF NOT EXISTS qualifier_source_value VARCHAR(50);
                ALTER TABLE measurement ADD COLUMN IF NOT EXISTS unit_source_concept_id INTEGER;
                ALTER TABLE measurement ADD COLUMN IF NOT EXISTS measurement_event_id BIGINT;
                ALTER TABLE measurement ADD COLUMN IF NOT EXISTS meas_event_field_concept_id INTEGER;
            """,
            reverse_sql="""
                ALTER TABLE measurement DROP COLUMN IF EXISTS meas_event_field_concept_id;
                ALTER TABLE measurement DROP COLUMN IF EXISTS measurement_event_id;
                ALTER TABLE measurement DROP COLUMN IF EXISTS unit_source_concept_id;
                ALTER TABLE measurement DROP COLUMN IF EXISTS qualifier_source_value;
                ALTER TABLE measurement DROP COLUMN IF EXISTS qualifier_concept_id;
                ALTER TABLE measurement DROP COLUMN IF EXISTS value_as_string;
                ALTER TABLE measurement DROP COLUMN IF EXISTS measurement_time;
                ALTER TABLE measurement DROP COLUMN IF EXISTS measurement_date;
            """
        ),
        # Make value_source_value nullable
        migrations.AlterField(
            model_name='measurement',
            name='value_source_value',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]

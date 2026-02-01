# Migration for OMOP CDM measurement table additions

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0028_add_behavior_fields'),
    ]

    operations = [
        # Add missing OMOP CDM measurement columns
        migrations.AddField(
            model_name='measurement',
            name='measurement_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='measurement',
            name='measurement_time',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='measurement',
            name='value_as_string',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='measurement',
            name='qualifier_concept_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='measurement',
            name='qualifier_source_value',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='measurement',
            name='unit_source_concept_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='measurement',
            name='measurement_event_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='measurement',
            name='meas_event_field_concept_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        # Make value_source_value nullable
        migrations.AlterField(
            model_name='measurement',
            name='value_source_value',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]

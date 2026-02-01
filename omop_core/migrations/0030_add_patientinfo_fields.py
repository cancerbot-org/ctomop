# Migration for additional PatientInfo fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0029_add_measurement_columns'),
    ]

    operations = [
        # Add patient_info fields that were added via SQL
        migrations.AddField(
            model_name='patientinfo',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]

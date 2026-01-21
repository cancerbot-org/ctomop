# Generated manually to add missing columns to patient_info table

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0018_remove_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientinfo',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True),
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

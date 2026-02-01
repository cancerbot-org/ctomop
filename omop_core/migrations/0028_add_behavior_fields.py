# Generated migration for Behavior tab fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0027_patientinfo_beta2_microglobulin_and_more'),
    ]

    operations = [
        # Lifestyle Factors
        migrations.AddField(
            model_name='patientinfo',
            name='smoking_status',
            field=models.CharField(blank=True, help_text='Smoking Status (Never/Former/Current)', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='pack_years',
            field=models.DecimalField(blank=True, decimal_places=1, help_text='Pack Years', max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='alcohol_use',
            field=models.CharField(blank=True, help_text='Alcohol Use (None/Light/Moderate/Heavy)', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='drinks_per_week',
            field=models.IntegerField(blank=True, help_text='Drinks per Week', null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='exercise_frequency',
            field=models.CharField(blank=True, help_text='Exercise Frequency', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='exercise_minutes_per_week',
            field=models.IntegerField(blank=True, help_text='Exercise Minutes per Week', null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='diet_type',
            field=models.CharField(blank=True, help_text='Diet Type', max_length=100, null=True),
        ),
        # Sleep & Wellbeing
        migrations.AddField(
            model_name='patientinfo',
            name='sleep_hours_per_night',
            field=models.DecimalField(blank=True, decimal_places=1, help_text='Average Sleep Hours per Night', max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='sleep_quality',
            field=models.CharField(blank=True, help_text='Sleep Quality', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='stress_level',
            field=models.CharField(blank=True, help_text='Stress Level', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='social_support',
            field=models.CharField(blank=True, help_text='Social Support', max_length=50, null=True),
        ),
        # Socioeconomic Factors
        migrations.AddField(
            model_name='patientinfo',
            name='employment_status',
            field=models.CharField(blank=True, help_text='Employment Status', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='education_level',
            field=models.CharField(blank=True, help_text='Education Level', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='marital_status',
            field=models.CharField(blank=True, help_text='Marital Status', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='insurance_type',
            field=models.CharField(blank=True, help_text='Insurance Type', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='number_of_dependents',
            field=models.IntegerField(blank=True, help_text='Number of Dependents', null=True),
        ),
        migrations.AddField(
            model_name='patientinfo',
            name='annual_household_income',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Annual Household Income (USD)', max_digits=12, null=True),
        ),
    ]

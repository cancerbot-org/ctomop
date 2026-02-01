# Migration to make ConditionOccurrence fields nullable

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0030_add_patientinfo_fields'),
    ]

    operations = [
        # Make basic fields nullable
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='condition_status_source_value',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='condition_source_value',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='stop_reason',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        # Make cancer-specific fields nullable
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='ajcc_clinical_m',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='ajcc_clinical_n',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='ajcc_clinical_stage',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='ajcc_clinical_t',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='ajcc_pathologic_m',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='ajcc_pathologic_n',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='ajcc_pathologic_stage',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='ajcc_pathologic_t',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='estrogen_receptor_status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='her2_status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='histologic_grade',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='nuclear_grade',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='progesterone_receptor_status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='staging_system',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='staging_system_version',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='conditionoccurrence',
            name='tumor_laterality',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]

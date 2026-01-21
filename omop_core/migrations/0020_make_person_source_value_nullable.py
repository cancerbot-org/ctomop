# Generated manually to make person_source_value nullable

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0019_add_missing_patientinfo_columns'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE person ALTER COLUMN person_source_value DROP NOT NULL;',
            reverse_sql='ALTER TABLE person ALTER COLUMN person_source_value SET NOT NULL;',
        ),
    ]

# Generated manually to fix gender_concept_id NOT NULL constraint

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0016_remove_person_birth_datetime_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE person ALTER COLUMN gender_concept_id DROP NOT NULL;',
            reverse_sql='ALTER TABLE person ALTER COLUMN gender_concept_id SET NOT NULL;',
        ),
    ]

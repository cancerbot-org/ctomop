# Generated manually to fix gender_concept_id NOT NULL constraint

from django.db import migrations, models
import django.db.models.deletion


def make_gender_concept_nullable(apps, schema_editor):
    """Make gender_concept_id nullable - works with both SQLite and PostgreSQL"""
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute('ALTER TABLE person ALTER COLUMN gender_concept_id DROP NOT NULL;')
    # SQLite doesn't need this - it's already nullable by default


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0016_remove_person_birth_datetime_and_more'),
    ]

    operations = [
        migrations.RunPython(make_gender_concept_nullable, migrations.RunPython.noop),
    ]

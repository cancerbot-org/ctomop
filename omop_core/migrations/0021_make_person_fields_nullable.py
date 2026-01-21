# Generated manually to make all person source fields nullable

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0020_make_person_source_value_nullable'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
                ALTER TABLE person ALTER COLUMN gender_source_value DROP NOT NULL;
                ALTER TABLE person ALTER COLUMN gender_source_concept_id DROP NOT NULL;
                ALTER TABLE person ALTER COLUMN race_source_value DROP NOT NULL;
                ALTER TABLE person ALTER COLUMN race_source_concept_id DROP NOT NULL;
                ALTER TABLE person ALTER COLUMN ethnicity_source_value DROP NOT NULL;
                ALTER TABLE person ALTER COLUMN ethnicity_source_concept_id DROP NOT NULL;
                ALTER TABLE person ALTER COLUMN secondary_languages DROP NOT NULL;
                ALTER TABLE person ALTER COLUMN language_skill_level DROP NOT NULL;
                ALTER TABLE person ALTER COLUMN year_of_birth DROP NOT NULL;
            ''',
            reverse_sql='''
                ALTER TABLE person ALTER COLUMN gender_source_value SET NOT NULL;
                ALTER TABLE person ALTER COLUMN gender_source_concept_id SET NOT NULL;
                ALTER TABLE person ALTER COLUMN race_source_value SET NOT NULL;
                ALTER TABLE person ALTER COLUMN race_source_concept_id SET NOT NULL;
                ALTER TABLE person ALTER COLUMN ethnicity_source_value SET NOT NULL;
                ALTER TABLE person ALTER COLUMN ethnicity_source_concept_id SET NOT NULL;
                ALTER TABLE person ALTER COLUMN secondary_languages SET NOT NULL;
                ALTER TABLE person ALTER COLUMN language_skill_level SET NOT NULL;
                ALTER TABLE person ALTER COLUMN year_of_birth SET NOT NULL;
            ''',
        ),
    ]

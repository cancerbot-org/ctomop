# Generated manually to make all person source fields nullable

from django.db import migrations


def make_person_fields_nullable_if_exist(apps, schema_editor):
    """Make person fields nullable only if they exist"""
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Get existing columns in person table
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='person'
        """)
        existing_columns = {row[0] for row in cursor.fetchall()}
        
        # List of columns to make nullable
        columns_to_modify = [
            'gender_source_value',
            'gender_source_concept_id',
            'race_source_value',
            'race_source_concept_id',
            'ethnicity_source_value',
            'ethnicity_source_concept_id',
            'secondary_languages',
            'language_skill_level',
            'year_of_birth'
        ]
        
        # Make each column nullable if it exists
        for column in columns_to_modify:
            if column in existing_columns:
                try:
                    cursor.execute(f"""
                        ALTER TABLE person 
                        ALTER COLUMN {column} DROP NOT NULL
                    """)
                except Exception as e:
                    # Column might already be nullable, continue
                    print(f"Could not modify {column}: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0020_make_person_source_value_nullable'),
    ]

    operations = [
        migrations.RunPython(make_person_fields_nullable_if_exist, migrations.RunPython.noop),
    ]

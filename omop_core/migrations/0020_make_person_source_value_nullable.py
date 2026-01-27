# Generated manually to make person_source_value nullable

from django.db import migrations


def make_column_nullable_if_exists(apps, schema_editor):
    """Make person_source_value nullable only if column exists"""
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='person' AND column_name='person_source_value'
        """)
        
        if cursor.fetchone():
            # Column exists, make it nullable
            cursor.execute("""
                ALTER TABLE person 
                ALTER COLUMN person_source_value DROP NOT NULL
            """)


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0019_add_missing_patientinfo_columns'),
    ]

    operations = [
        migrations.RunPython(make_column_nullable_if_exists, migrations.RunPython.noop),
    ]

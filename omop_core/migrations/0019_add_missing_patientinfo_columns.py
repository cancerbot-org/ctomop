# Generated manually to add missing columns to patient_info table

from django.db import migrations, models


def add_columns_if_not_exist(apps, schema_editor):
    """Add columns only if they don't already exist"""
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Get existing columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='patient_info'
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Add email if it doesn't exist
        if 'email' not in existing_columns:
            cursor.execute("""
                ALTER TABLE patient_info 
                ADD COLUMN email VARCHAR(255) NULL
            """)
        
        # Add date_of_birth if it doesn't exist
        if 'date_of_birth' not in existing_columns:
            cursor.execute("""
                ALTER TABLE patient_info 
                ADD COLUMN date_of_birth DATE NULL
            """)
        
        # Add created_at if it doesn't exist
        if 'created_at' not in existing_columns:
            cursor.execute("""
                ALTER TABLE patient_info 
                ADD COLUMN created_at TIMESTAMP NULL
            """)
        
        # Add updated_at if it doesn't exist
        if 'updated_at' not in existing_columns:
            cursor.execute("""
                ALTER TABLE patient_info 
                ADD COLUMN updated_at TIMESTAMP NULL
            """)


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0018_remove_phone_number'),
    ]

    operations = [
        migrations.RunPython(add_columns_if_not_exist, migrations.RunPython.noop),
    ]

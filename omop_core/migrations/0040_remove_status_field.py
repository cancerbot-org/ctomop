from django.db import migrations


class Migration(migrations.Migration):
    """
    Remove 'status' field from PatientInfo model state.
    The column never existed in the DB, so we only update Django's migration state.
    """

    dependencies = [
        ("omop_core", "0039_remove_ki67_percentage"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],  # No DB change needed - column never existed
            state_operations=[
                migrations.RemoveField(
                    model_name="patientinfo",
                    name="status",
                ),
            ],
        ),
    ]

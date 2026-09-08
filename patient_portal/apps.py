from django.apps import AppConfig


class PatientPortalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "patient_portal"

    def ready(self):
        # Registers the system checks; the import is the registration (#146).
        from . import checks  # noqa: F401

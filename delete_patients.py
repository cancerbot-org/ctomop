#!/usr/bin/env python
"""Delete all patient data"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from omop_core.models import PatientInfo, Person, Measurement, ConditionOccurrence, DrugExposure, ProcedureOccurrence
from django.contrib.auth.models import User

print("Deleting all patient data...")
DrugExposure.objects.all().delete()
print("  Deleted DrugExposure records")
ProcedureOccurrence.objects.all().delete()
print("  Deleted ProcedureOccurrence records")
PatientInfo.objects.all().delete()
print("  Deleted PatientInfo records")
Measurement.objects.all().delete()
print("  Deleted Measurement records")
ConditionOccurrence.objects.all().delete()
print("  Deleted ConditionOccurrence records")

# Delete patient users (ID > 1000 to avoid deleting admin users)
try:
    User.objects.filter(id__gte=1000).delete()
    print("  Deleted User records")
except Exception as e:
    print(f"  Skipping User deletion: {e}")

# Use raw SQL to delete Person records to avoid cascade issues
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("DELETE FROM person")
print("  Deleted Person records")
print("\nAll patient data deleted successfully")

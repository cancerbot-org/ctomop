#!/usr/bin/env python
"""Test script to verify upload_fhir API extracts names and therapies"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from omop_core.models import Person, PatientInfo

print("Current patients in database:")
patients = PatientInfo.objects.all().order_by('person_id')[:5]
for p in patients:
    print(f"\nPatient {p.person.person_id}:")
    print(f"  Name: {p.person.given_name} {p.person.family_name}")
    print(f"  First line therapy: {p.first_line_therapy}")
    print(f"  Therapy lines: {p.therapy_lines_count}")
    print(f"  Refractory status: {p.treatment_refractory_status}")

print(f"\nTotal patients: {PatientInfo.objects.count()}")

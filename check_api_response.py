#!/usr/bin/env python
"""Check what the API is actually returning"""
import django
import os
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from patient_portal.api.serializers import PatientInfoSerializer
from omop_core.models import PatientInfo

print("API Response Check:\n")
print("=" * 70)

for patient in PatientInfo.objects.all().order_by('person_id')[:3]:
    serializer = PatientInfoSerializer(patient)
    data = serializer.data
    
    print(f"\nPatient {data['person_id']}: {data['patient_name']}")
    print(f"  Disease: {data.get('disease')}")
    print(f"  First Line Therapy: {data.get('first_line_therapy')}")
    print(f"  First Line Date: {data.get('first_line_date')}")
    print(f"  First Line Outcome: {data.get('first_line_outcome')}")
    print(f"  Second Line Therapy: {data.get('second_line_therapy')}")
    print(f"  Later Therapy: {data.get('later_therapy')}")
    
print("\n" + "=" * 70)
print("\nJSON output for first patient:")
patient = PatientInfo.objects.first()
serializer = PatientInfoSerializer(patient)
print(json.dumps({
    'person_id': serializer.data['person_id'],
    'patient_name': serializer.data['patient_name'],
    'disease': serializer.data.get('disease'),
    'first_line_therapy': serializer.data.get('first_line_therapy'),
    'first_line_date': serializer.data.get('first_line_date'),
    'first_line_outcome': serializer.data.get('first_line_outcome'),
}, indent=2))

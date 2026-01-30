#!/usr/bin/env python
"""Check computed therapy fields for all patients"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from omop_core.models import PatientInfo

print("Computed Therapy Fields Summary:\n")
for p in PatientInfo.objects.all().order_by('person_id'):
    print(f"Patient {p.person_id}:")
    print(f"  Therapy lines: {p.therapy_lines_count}")
    print(f"  Prior therapy: {p.prior_therapy}")
    print(f"  Relapse count: {p.relapse_count}")
    print(f"  Refractory status: {p.treatment_refractory_status}")
    print(f"  Lines: ", end='')
    if p.first_line_therapy:
        print(f"1st: {p.first_line_therapy} ({p.first_line_outcome or 'no outcome'})", end='')
    if p.second_line_therapy:
        print(f", 2nd: {p.second_line_therapy} ({p.second_line_outcome or 'no outcome'})", end='')
    if p.later_therapy:
        print(f", Later: {p.later_therapy} ({p.later_outcome or 'no outcome'})", end='')
    print()
    print()

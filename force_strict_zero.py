import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from omop_core.models import PatientInfo

patients = PatientInfo.objects.all()
updated_count = 0

success_outcomes = [
    'Complete Response', 'Complete Response (CR)',
    'Stringent Complete Response (sCR)',
    'Very Good Partial Response (VGPR)'
]

for p in patients:
    relapse = 0
    if p.first_line_outcome in success_outcomes and p.second_line_therapy:
        relapse += 1
    if p.second_line_outcome in success_outcomes and p.later_therapy:
        relapse += 1

    # We want to force the new default on everyone unless they already had a manual string override.
    # Because previously the default was None and now it's 0.
    if p.relapse_count is None or p.relapse_count == relapse:
        p.relapse_count = relapse
        p.save()
        updated_count += 1
    else:
        # If it was overridden manually, keep their manual value
        pass

print(f"Updated relapse count setting to strict 0 when missing relapses: {updated_count} patients affected.")
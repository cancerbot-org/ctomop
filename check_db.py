import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()
from omop_core.models import PatientInfo
patients = PatientInfo.objects.all()
zero_count = sum(1 for p in patients if p.relapse_count == 0)
none_count = sum(1 for p in patients if p.relapse_count is None)
other_count = sum(1 for p in patients if p.relapse_count not in [0, None])
print(f"Total: {len(patients)}")
print(f"Zero: {zero_count}")
print(f"None/Empty: {none_count}")
print(f"Other (>0): {other_count}")

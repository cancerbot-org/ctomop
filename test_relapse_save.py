import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()
from omop_core.models import PatientInfo
p = PatientInfo.objects.first()
print(f"Original: {p.relapse_count}")
p.relapse_count = 99
p.save()
p.refresh_from_db()
print(f"After manual edit: {p.relapse_count}")

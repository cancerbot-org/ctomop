import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()
from omop_core.models import PatientInfo
from django.db.models import Count

counts = PatientInfo.objects.values('relapse_count').annotate(total=Count('id'))
for c in counts:
    print(f"Relapse Count {c['relapse_count']}: {c['total']} patients")

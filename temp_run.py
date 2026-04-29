import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()
from omop_core.models import PatientInfo
count = 0
for p in PatientInfo.objects.all():
    p.save()
    count += 1
print(f'Done saving {count} patients.')

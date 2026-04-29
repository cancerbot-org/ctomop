import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from omop_core.models import PatientInfo

HISTOLOGIC_TYPE_OPTIONS = [
  'Unknown',
  'Infiltrating ductal carcinoma (IDC)',
  'Ductal carcinoma in situ (DCIS)',
  'Infiltrating lobular carcinoma (ILC)',
  'Lobular carcinoma in situ (LCIS)',
  'Mixed ductal and lobular carcinoma',
  'Mucinous (colloid) carcinoma',
  'Tubular carcinoma',
  'Medullary carcinoma',
  'Papillary carcinoma',
  'Metaplastic carcinoma',
  'Paget disease of the nipple',
  'Inflammatory carcinoma'
]

updated_count = 0
for p in PatientInfo.objects.all():
    if not p.histologic_type or p.histologic_type not in HISTOLOGIC_TYPE_OPTIONS:
        p.histologic_type = random.choice(HISTOLOGIC_TYPE_OPTIONS)
        p.save()
        updated_count += 1

print(f"Updated {updated_count} patients with valid Histologic Types.")

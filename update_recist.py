"""
One-off script: recompute measurable_disease_by_recist_status for all PatientInfo records
based on existing tumor_stage, distant_metastasis_stage, and metastasis_status fields.

Logic:
  - metastasis_status == "Positive" OR tumor_stage starts with T3/T4 → True
  - metastasis_status == "Unknown" (and no clear T3/T4) → None (Unknown)
  - metastasis_status == "Negative" with early T-stage, or clearly non-metastatic → False
  - No staging data at all → None (Unknown)

Run with:
  DATABASE_URL="..." .venv/bin/python update_recist.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from omop_core.models import PatientInfo

updated = {'True': 0, 'False': 0, 'None': 0, 'unchanged': 0}

for pi in PatientInfo.objects.all():
    t_stage = pi.tumor_stage or ''
    m_stage = pi.distant_metastasis_stage or ''
    m_status = pi.metastasis_status or ''

    has_staging = bool(t_stage or m_stage or m_status)

    if not has_staging:
        new_val = None
    elif m_status == 'Positive' or 'M1' in m_stage or any(t_stage.startswith(t) for t in ['T3', 'T4']):
        new_val = True
    elif m_status == 'Unknown':
        new_val = None
    else:
        new_val = False

    if pi.measurable_disease_by_recist_status != new_val:
        pi.measurable_disease_by_recist_status = new_val
        pi.save(update_fields=['measurable_disease_by_recist_status'])
        updated[str(new_val)] += 1
    else:
        updated['unchanged'] += 1

print(f"Set to True:  {updated['True']}")
print(f"Set to False: {updated['False']}")
print(f"Set to None:  {updated['None']}")
print(f"Unchanged:    {updated['unchanged']}")

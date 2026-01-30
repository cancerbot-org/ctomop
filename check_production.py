import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from omop_core.models import PatientInfo

# Check a few production patients
patients = PatientInfo.objects.filter(person_id__in=[1021, 1022, 1027]).order_by('person_id')
for p in patients:
    print(f'\nPatient {p.person_id}:')
    print(f'  First line: {p.first_line_therapy} - Outcome: {p.first_line_outcome}')
    print(f'  Second line: {p.second_line_therapy} - Outcome: {p.second_line_outcome}')
    print(f'  Later line: {p.later_therapy} - Outcome: {p.later_outcome}')
    print(f'  Computed: Lines={p.therapy_lines_count}, Prior={p.prior_therapy}, Refractory={p.treatment_refractory_status}')

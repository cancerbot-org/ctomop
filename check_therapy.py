import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()
from omop_core.models import PatientInfo

print('Therapy Line Distribution:\n')
patients = PatientInfo.objects.all()

therapy_counts = {0: 0, 1: 0, 2: 0, 3: 0}

for p in patients:
    lines = 0
    if p.first_line_therapy:
        lines = 1
    if p.second_line_therapy:
        lines = 2
    if p.later_therapy:
        lines = 3
    
    therapy_counts[lines] += 1
    print(f'Patient {p.person.person_id}: {lines} line(s)')
    if lines > 0:
        print(f'  Line 1: {p.first_line_therapy} ({p.first_line_date})')
    if lines > 1:
        print(f'  Line 2: {p.second_line_therapy} ({p.second_line_date})')
    if lines > 2:
        print(f'  Line 3: {p.later_therapy} ({p.later_date})')

print('\n' + '='*60)
print('Distribution Summary:')
print(f'  Treatment-naive (0 lines): {therapy_counts[0]} ({therapy_counts[0]/10*100:.0f}%)')
print(f'  1 line: {therapy_counts[1]} ({therapy_counts[1]/10*100:.0f}%)')
print(f'  2 lines: {therapy_counts[2]} ({therapy_counts[2]/10*100:.0f}%)')
print(f'  3 lines: {therapy_counts[3]} ({therapy_counts[3]/10*100:.0f}%)')

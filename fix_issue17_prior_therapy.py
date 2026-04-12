"""
Fix issue #17: Update prior_therapy values to use correct vocabulary.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from django.db.models import Count
from omop_core.models import PatientInfo

patients = PatientInfo.objects.all()
fixed = 0
for p in patients:
    lines = p.therapy_lines_count or 0
    if lines == 0:
        expected = 'None'
    elif lines == 1:
        expected = 'One line'
    elif lines == 2:
        expected = 'Two lines'
    else:
        expected = 'More than two lines of therapy'
    if p.prior_therapy != expected:
        p.prior_therapy = expected
        p.save(update_fields=['prior_therapy'])
        fixed += 1

print(f'Fixed {fixed} records')
print('Distribution after fix:')
for row in PatientInfo.objects.values('prior_therapy').annotate(n=Count('id')).order_by('prior_therapy'):
    print(f"  {row['prior_therapy']!r}: {row['n']}")

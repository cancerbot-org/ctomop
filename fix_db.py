import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from omop_core.models import PatientInfo
patients = PatientInfo.objects.all()

success_outcomes = [
    'Complete Response', 'Complete Response (CR)',
    'Stringent Complete Response (sCR)',
    'Very Good Partial Response (VGPR)',
    'Partial Response (PR)', 'Partial Response'
]

updated = 0

for p in patients:
    changed = False
    
    # Fix discontinuation -> outcome logic
    if p.first_line_discontinuation_reason == 'Progression' and p.first_line_outcome not in ['Progressive Disease', 'Progressive Disease (PD)']:
        p.first_line_outcome = 'Progressive Disease (PD)'
        changed = True
    if p.second_line_discontinuation_reason == 'Progression' and p.second_line_outcome not in ['Progressive Disease', 'Progressive Disease (PD)']:
        p.second_line_outcome = 'Progressive Disease (PD)'
        changed = True
    if p.later_discontinuation_reason == 'Progression' and p.later_outcome not in ['Progressive Disease', 'Progressive Disease (PD)']:
        p.later_outcome = 'Progressive Disease (PD)'
        changed = True

    # Recompute relapse count correctly and FORCE it
    relapse = 0
    if p.first_line_outcome in success_outcomes and p.second_line_therapy:
        relapse += 1
    if p.second_line_outcome in success_outcomes and p.later_therapy:
        relapse += 1
        
    if p.relapse_count != relapse:
        p.relapse_count = relapse
        changed = True
        
    if changed or (p.person and p.person.person_id == 20300):
        # We manually bypass the fallback check in save() since we know we want
        # this value to stick
        p.save()
        updated += 1

print(f"Fixed {updated} patients.")
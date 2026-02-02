import json

with open('data/synthetic_patients_100.json', 'r') as f:
    bundle = json.load(f)

# Count regimens (therapy lines) and observations by patient
patient_data = {}
for entry in bundle.get('entry', []):
    resource = entry.get('resource', {})
    resource_type = resource.get('resourceType')
    
    if resource_type == 'MedicationStatement':
        # Only count regimens (therapy lines), not individual drugs
        # Regimens have IDs like "regimen-1-line1", drugs have "drug-1-line1-DrugName"
        resource_id = resource.get('id', '')
        if resource_id.startswith('regimen-'):
            patient_ref = resource.get('subject', {}).get('reference', '')
            patient_id = patient_ref.split('/')[-1]
            if patient_id not in patient_data:
                patient_data[patient_id] = {'therapy_lines': 0, 'intent': 0, 'discontinuation': 0}
            patient_data[patient_id]['therapy_lines'] += 1
    
    elif resource_type == 'Observation':
        code = resource.get('code', {}).get('coding', [{}])[0].get('code', '')
        patient_ref = resource.get('subject', {}).get('reference', '')
        patient_id = patient_ref.split('/')[-1]
        if patient_id not in patient_data:
            patient_data[patient_id] = {'therapy_lines': 0, 'intent': 0, 'discontinuation': 0}
        
        if code == '42804-5':  # Therapy Intent
            patient_data[patient_id]['intent'] += 1
        elif code == '91379-3':  # Discontinuation
            patient_data[patient_id]['discontinuation'] += 1

# Show first 15 patients with therapy
print('Patient therapy line counts:')
print('Patient | Therapy Lines | Intent Obs | Discontinuation Obs | Status')
print('-' * 75)
for pid in sorted(patient_data.keys(), key=lambda x: int(x) if x.isdigit() else 0)[:20]:
    data = patient_data[pid]
    lines = data['therapy_lines']
    if lines == 0:
        continue  # Skip patients with no therapy
    intent = data['intent']
    disc = data['discontinuation']
    # Expected: intent == lines, disc == lines - 1 (last line has no discontinuation)
    match = '✓' if intent == lines and disc == lines - 1 else '✗'
    print(f'{pid:7} | {lines:13} | {intent:10} | {disc:19} | {match:6}')

print('\n✓ = Correct: Intent count = Therapy Lines, Discontinuation = Therapy Lines - 1')
print('(Last/current therapy line should not have discontinuation reason)')

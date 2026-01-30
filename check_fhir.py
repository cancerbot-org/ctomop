import json

with open('data/test_patients.json', 'r') as f:
    data = json.load(f)

# Check first patient
for entry in data['entry']:
    resource = entry['resource']
    if resource['resourceType'] == 'Patient':
        print('PATIENT EXTENSIONS:')
        for ext in resource.get('extension', []):
            url = ext.get('url', '')
            if 'ecog' in url.lower():
                print(f'  ECOG: {ext.get("valueInteger")}')
            elif 'weight' in url.lower():
                val = ext.get('valueQuantity', {})
                print(f'  Weight: {val.get("value")} {val.get("unit")}')
            elif 'height' in url.lower():
                val = ext.get('valueQuantity', {})
                print(f'  Height: {val.get("value")} {val.get("unit")}')
            elif 'systolic' in url.lower():
                val = ext.get('valueQuantity', {})
                print(f'  Systolic: {val.get("value")}')
            elif 'diastolic' in url.lower():
                val = ext.get('valueQuantity', {})
                print(f'  Diastolic: {val.get("value")}')
            elif 'heartRate' in url:
                val = ext.get('valueQuantity', {})
                print(f'  Heart Rate: {val.get("value")}')
        break

print()
for entry in data['entry']:
    resource = entry['resource']
    if resource['resourceType'] == 'Condition':
        print('CONDITION:')
        print(f'  Histologic: {resource.get("code", {}).get("text")}')
        stage_arr = resource.get('stage', [])
        if stage_arr:
            stage_code = stage_arr[0].get('summary', {}).get('coding', [{}])[0].get('code')
            print(f'  Stage: {stage_code}')
        break

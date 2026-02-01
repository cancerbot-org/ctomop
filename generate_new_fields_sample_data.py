#!/usr/bin/env python3
"""
Generate sample FHIR observations for new cancer assessment, treatment, and lab fields
"""

import json
import random
from datetime import datetime, timedelta

# Load existing bundle
with open('data/sample_patients_with_blood_counts.json', 'r') as f:
    bundle = json.load(f)

# Extract patient IDs
patient_ids = []
for entry in bundle['entry']:
    if entry['resource']['resourceType'] == 'Patient':
        patient_ids.append(entry['resource']['id'])

print(f"Found {len(patient_ids)} patients")

# LOINC codes for new fields
LOINC_CODES = {
    'ecog_status': '89247-1',  # ECOG Performance Status
    'test_methodology': '85337-4',  # Genetic test methodology
    'test_specimen_type': '31208-2',  # Specimen source
    'report_interpretation': '69548-6',  # Genetic test interpretation
    'oncotype_dx': '85337-4',  # Oncotype DX score
    'ki67': '94638-6',  # Ki-67
    'androgen_receptor': '16112-5',  # Androgen receptor
    'therapy_intent': '42804-5',  # Therapeutic intent
    'reason_discontinuation': '91379-3',  # Reason for discontinuation
    'ldh': '14804-9',  # LDH
    'alkaline_phosphatase': '6768-6',  # Alkaline phosphatase
    'magnesium': '2601-3',  # Magnesium
    'phosphorus': '2777-1',  # Phosphorus
    'pregnancy_test': '2106-3',  # Pregnancy test
}

def random_date_in_past_year():
    days_ago = random.randint(1, 365)
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime('%Y-%m-%d')

def generate_observation(patient_id, loinc_code, display_name, value, unit=None):
    """Generate a numeric observation"""
    obs_id = f"obs-{loinc_code}-{patient_id}"
    observation = {
        "fullUrl": f"urn:uuid:{obs_id}",
        "resource": {
            "resourceType": "Observation",
            "id": obs_id,
            "status": "final",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": loinc_code,
                    "display": display_name
                }]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": random_date_in_past_year(),
            "valueQuantity": {
                "value": value,
                "unit": unit if unit else "",
                "system": "http://unitsofmeasure.org",
                "code": unit if unit else ""
            }
        }
    }
    return observation

def generate_codeable_observation(patient_id, loinc_code, display_name, value_text):
    """Generate a CodeableConcept observation"""
    obs_id = f"obs-{loinc_code}-{patient_id}"
    observation = {
        "fullUrl": f"urn:uuid:{obs_id}",
        "resource": {
            "resourceType": "Observation",
            "id": obs_id,
            "status": "final",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": loinc_code,
                    "display": display_name
                }]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": random_date_in_past_year(),
            "valueCodeableConcept": {
                "text": value_text
            }
        }
    }
    return observation

# Generate observations for all patients
new_observations = []

for patient_id in patient_ids:
    # ECOG Status (0-4)
    ecog_score = random.choice([0, 0, 1, 1, 1, 2, 2, 3])
    new_observations.append(generate_observation(
        patient_id, LOINC_CODES['ecog_status'], 'ECOG Performance Status', ecog_score
    ))
    
    # Test Methodology
    methodology = random.choice(['NGS', 'IHC', 'FISH', 'PCR'])
    new_observations.append(generate_codeable_observation(
        patient_id, LOINC_CODES['test_methodology'], 'Test Methodology', methodology
    ))
    
    # Test Specimen Type
    specimen_type = random.choice(['Primary Biopsy', 'Metastatic Biopsy', 'Primary Biopsy'])
    new_observations.append(generate_codeable_observation(
        patient_id, LOINC_CODES['test_specimen_type'], 'Specimen Source', specimen_type
    ))
    
    # Report Interpretation
    interpretation = random.choice(['Positive', 'Negative', 'Indeterminate', 'Not Tested', 'Positive', 'Negative'])
    new_observations.append(generate_codeable_observation(
        patient_id, LOINC_CODES['report_interpretation'], 'Test Interpretation', interpretation
    ))
    
    # Oncotype DX Score (0-100)
    if random.random() > 0.3:  # 70% have this test
        oncotype_score = random.randint(5, 45)
        new_observations.append(generate_observation(
            patient_id, LOINC_CODES['oncotype_dx'], 'Oncotype DX Score', oncotype_score
        ))
    
    # Ki-67 Percentage (0-100%)
    ki67 = round(random.uniform(5.0, 80.0), 1)
    new_observations.append(generate_observation(
        patient_id, LOINC_CODES['ki67'], 'Ki-67', ki67, '%'
    ))
    
    # Androgen Receptor Status
    ar_status = random.choice(['Positive', 'Negative', 'Positive', 'Positive'])
    new_observations.append(generate_codeable_observation(
        patient_id, LOINC_CODES['androgen_receptor'], 'Androgen Receptor Status', ar_status
    ))
    
    # Therapy Intent
    therapy_intent = random.choice(['Adjuvant', 'Neoadjuvant', 'Metastatic', 'Adjuvant', 'Adjuvant'])
    new_observations.append(generate_codeable_observation(
        patient_id, LOINC_CODES['therapy_intent'], 'Therapy Intent', therapy_intent
    ))
    
    # Reason for Discontinuation (only for some patients)
    if random.random() > 0.6:  # 40% have discontinued treatment
        reason = random.choice(['Progression', 'Toxicity', 'Completion', 'Progression'])
        new_observations.append(generate_codeable_observation(
            patient_id, LOINC_CODES['reason_discontinuation'], 'Reason for Discontinuation', reason
        ))
    
    # LDH (100-600 U/L, normal 140-280)
    ldh = random.randint(120, 550)
    new_observations.append(generate_observation(
        patient_id, LOINC_CODES['ldh'], 'Lactate Dehydrogenase', ldh, 'U/L'
    ))
    
    # Alkaline Phosphatase (30-120 U/L)
    alp = random.randint(35, 180)
    new_observations.append(generate_observation(
        patient_id, LOINC_CODES['alkaline_phosphatase'], 'Alkaline Phosphatase', alp, 'U/L'
    ))
    
    # Magnesium (1.5-2.5 mg/dL)
    mag = round(random.uniform(1.4, 2.6), 1)
    new_observations.append(generate_observation(
        patient_id, LOINC_CODES['magnesium'], 'Magnesium', mag, 'mg/dL'
    ))
    
    # Phosphorus (2.5-4.5 mg/dL)
    phos = round(random.uniform(2.3, 4.8), 1)
    new_observations.append(generate_observation(
        patient_id, LOINC_CODES['phosphorus'], 'Phosphorus', phos, 'mg/dL'
    ))
    
    # Pregnancy Test (for female patients)
    if random.random() > 0.5:  # Assume 50% are female of childbearing age
        preg_result = random.choice(['Negative', 'Negative', 'Negative', 'Negative', 'Positive'])
        new_observations.append(generate_codeable_observation(
            patient_id, LOINC_CODES['pregnancy_test'], 'Pregnancy Test', preg_result
        ))

# Add new observations to bundle
bundle['entry'].extend(new_observations)

print(f"\nGenerated {len(new_observations)} new observations")
print(f"Total resources in bundle: {len(bundle['entry'])}")

# Save updated bundle
with open('data/sample_patients_with_blood_counts.json', 'w') as f:
    json.dump(bundle, f, indent=2)

print("\n✓ Updated FHIR bundle saved")

# Verify counts
print("\nObservation counts by type:")
loinc_counts = {
    'ECOG Status': LOINC_CODES['ecog_status'],
    'Test Methodology': LOINC_CODES['test_methodology'],
    'Specimen Type': LOINC_CODES['test_specimen_type'],
    'Report Interpretation': LOINC_CODES['report_interpretation'],
    'Oncotype DX': LOINC_CODES['oncotype_dx'],
    'Ki-67': LOINC_CODES['ki67'],
    'Androgen Receptor': LOINC_CODES['androgen_receptor'],
    'Therapy Intent': LOINC_CODES['therapy_intent'],
    'LDH': LOINC_CODES['ldh'],
    'Alkaline Phosphatase': LOINC_CODES['alkaline_phosphatase'],
    'Magnesium': LOINC_CODES['magnesium'],
    'Phosphorus': LOINC_CODES['phosphorus'],
    'Pregnancy Test': LOINC_CODES['pregnancy_test'],
}

for name, loinc_code in loinc_counts.items():
    count = 0
    for entry in bundle['entry']:
        if entry['resource']['resourceType'] == 'Observation':
            obs = entry['resource']
            if obs.get('code', {}).get('coding'):
                for coding in obs['code']['coding']:
                    if coding.get('code') == loinc_code:
                        count += 1
                        break
    print(f"✓ {name} (LOINC {loinc_code}): {count} observations")

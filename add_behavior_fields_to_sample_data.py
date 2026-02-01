#!/usr/bin/env python3
"""
Script to add behavior-related observations to the FHIR sample data.
Adds: contraceptive use, consent capability, caregiver availability, 
mental health disorders, substance use, and geographic exposure risk.
"""

import json
import random
from datetime import datetime, timedelta

# Load the existing bundle
with open('data/sample_patients_with_blood_counts.json', 'r') as f:
    bundle = json.load(f)

# Extract patient IDs
patient_ids = []
for entry in bundle['entry']:
    if entry['resource']['resourceType'] == 'Patient':
        patient_ids.append(entry['resource']['id'])

print(f"Found {len(patient_ids)} patients")

# Generate a random date within the last year
def random_date():
    days_ago = random.randint(0, 365)
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime('%Y-%m-%d')

new_observations = []
observation_id = 1000  # Starting ID for new observations

for patient_id in patient_ids:
    try:
        patient_num = int(patient_id)
    except:
        # Handle different ID formats
        if '-' in str(patient_id):
            patient_num = int(str(patient_id).split('-')[1])
        else:
            patient_num = int(patient_id)
    
    # 1. Contraceptive Use (8659-8) - 50% Yes for females
    if patient_num % 2 == 0:  # Assume even IDs are female
        contraceptive_value = "Yes" if random.random() < 0.5 else "No"
        new_observations.append({
            "fullUrl": f"urn:uuid:obs-contraceptive-{patient_id}",
            "resource": {
                "resourceType": "Observation",
                "id": f"obs-contraceptive-{patient_id}",
                "status": "final",
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "8659-8",
                        "display": "Contraceptive use"
                    }],
                    "text": "Contraceptive Use"
                },
                "subject": {
                    "reference": f"Patient/{patient_id}"
                },
                "effectiveDateTime": random_date(),
                "valueCodeableConcept": {
                    "text": contraceptive_value
                }
            }
        })
    
    # 2. Ability to Consent (75985-6) - Default Yes (90% Yes)
    consent_value = "Yes" if random.random() < 0.9 else "No"
    new_observations.append({
        "fullUrl": f"urn:uuid:obs-consent-{patient_id}",
        "resource": {
            "resourceType": "Observation",
            "id": f"obs-consent-{patient_id}",
            "status": "final",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "75985-6",
                    "display": "Ability to consent"
                }],
                "text": "Ability to Consent"
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": random_date(),
            "valueCodeableConcept": {
                "text": consent_value
            }
        }
    })
    
    # 3. Caregiver Availability (74014-2) - Default Yes (85% Yes)
    caregiver_value = "Yes" if random.random() < 0.85 else "No"
    new_observations.append({
        "fullUrl": f"urn:uuid:obs-caregiver-{patient_id}",
        "resource": {
            "resourceType": "Observation",
            "id": f"obs-caregiver-{patient_id}",
            "status": "final",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "74014-2",
                    "display": "Caregiver availability"
                }],
                "text": "Availability of Caregiver"
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": random_date(),
            "valueCodeableConcept": {
                "text": caregiver_value
            }
        }
    })
    
    # 4. Mental Health Disorders (75618-3) - Default No (20% Yes)
    mental_health_value = "Yes" if random.random() < 0.2 else "No"
    new_observations.append({
        "fullUrl": f"urn:uuid:obs-mental-health-{patient_id}",
        "resource": {
            "resourceType": "Observation",
            "id": f"obs-mental-health-{patient_id}",
            "status": "final",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "75618-3",
                    "display": "Mental health disorders"
                }],
                "text": "Mental Health Disorders"
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": random_date(),
            "valueCodeableConcept": {
                "text": mental_health_value
            }
        }
    })
    
    # 5. Non-prescription Drug Use (74204-0) - Default No (15% Yes)
    drug_use_value = "Yes" if random.random() < 0.15 else "No"
    obs = {
        "fullUrl": f"urn:uuid:obs-drug-use-{patient_id}",
        "resource": {
            "resourceType": "Observation",
            "id": f"obs-drug-use-{patient_id}",
            "status": "final",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "74204-0",
                    "display": "Non-prescription drug use"
                }],
                "text": "Non-prescription Recreational Drug Use"
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": random_date(),
            "valueCodeableConcept": {
                "text": drug_use_value
            }
        }
    }
    if drug_use_value == "Yes":
        obs["resource"]["note"] = [{
            "text": random.choice(["Occasional marijuana use", "Social cannabis use", "Former recreational use"])
        }]
    new_observations.append(obs)
    
    # 6. Geographic/Environmental Exposure Risk (82593-5) - Default No (10% Yes)
    exposure_value = "Yes" if random.random() < 0.1 else "No"
    obs = {
        "fullUrl": f"urn:uuid:obs-exposure-{patient_id}",
        "resource": {
            "resourceType": "Observation",
            "id": f"obs-exposure-{patient_id}",
            "status": "final",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "82593-5",
                    "display": "Environmental exposure"
                }],
                "text": "Geographic/Occupational/Environmental/Infectious Disease Exposure Risk"
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": random_date(),
            "valueCodeableConcept": {
                "text": exposure_value
            }
        }
    }
    if exposure_value == "Yes":
        obs["resource"]["note"] = [{
            "text": random.choice([
                "Occupational asbestos exposure",
                "Previous travel to endemic malaria region",
                "Environmental exposure to pesticides",
                "Occupational chemical exposure"
            ])
        }]
    new_observations.append(obs)

# Add all new observations to the bundle
bundle['entry'].extend(new_observations)

# Update the total count
bundle['total'] = len(bundle['entry'])

# Write the updated bundle back to the file
with open('data/sample_patients_with_blood_counts.json', 'w') as f:
    json.dump(bundle, f, indent=2)

print(f"Generated {len(new_observations)} new observations")
print(f"Updated bundle now has {bundle['total']} total resources")
print("Sample data file updated successfully!")

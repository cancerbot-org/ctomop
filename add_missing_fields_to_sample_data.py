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

# Helper function to generate random date in past year
def random_date():
    days_ago = random.randint(1, 365)
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime('%Y-%m-%d')

# LOINC codes for the new observations
observations_to_add = []

for patient_id in patient_ids:
    try:
        patient_num = int(patient_id)
    except:
        # Handle different ID formats
        if '-' in str(patient_id):
            patient_num = int(str(patient_id).split('-')[1])
        else:
            patient_num = int(patient_id)
    
    # 1. ECOG Assessment Date (89247-1) - just update existing ECOG to have a date
    # This is already handled by having effectiveDateTime on ECOG observations
    
    # 2. Test Methodology (85337-4) - for genetic testing
    observations_to_add.append({
        "fullUrl": f"urn:uuid:test-methodology-{patient_num}",
        "resource": {
            "resourceType": "Observation",
            "id": f"test-methodology-{patient_num}",
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory",
                    "display": "Laboratory"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "85337-4",
                    "display": "Test Methodology"
                }],
                "text": "Test Methodology"
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": random_date(),
            "valueCodeableConcept": {
                "coding": [{
                    "code": random.choice(["NGS", "IHC", "FISH", "PCR"]),
                    "display": random.choice(["Next Generation Sequencing", "Immunohistochemistry", "Fluorescence In Situ Hybridization", "Polymerase Chain Reaction"])
                }],
                "text": random.choice(["NGS", "IHC", "FISH", "PCR"])
            }
        }
    })
    
    # 3. Test Specimen Type (31208-2)
    observations_to_add.append({
        "fullUrl": f"urn:uuid:test-specimen-{patient_num}",
        "resource": {
            "resourceType": "Observation",
            "id": f"test-specimen-{patient_num}",
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory",
                    "display": "Laboratory"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "31208-2",
                    "display": "Specimen Source"
                }],
                "text": "Specimen Source"
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": random_date(),
            "valueCodeableConcept": {
                "coding": [{
                    "code": random.choice(["primary", "metastatic"]),
                    "display": random.choice(["Primary Tumor Biopsy", "Metastatic Tumor Biopsy"])
                }],
                "text": random.choice(["Primary Biopsy", "Metastatic Biopsy"])
            }
        }
    })
    
    # 4. Report Interpretation (69548-6)
    observations_to_add.append({
        "fullUrl": f"urn:uuid:report-interpretation-{patient_num}",
        "resource": {
            "resourceType": "Observation",
            "id": f"report-interpretation-{patient_num}",
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory",
                    "display": "Laboratory"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "69548-6",
                    "display": "Test Interpretation"
                }],
                "text": "Test Interpretation"
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": random_date(),
            "valueCodeableConcept": {
                "coding": [{
                    "code": random.choice(["positive", "negative", "indeterminate", "not_tested"]),
                    "display": random.choice(["Positive", "Negative", "Indeterminate", "Not Tested"])
                }],
                "text": random.choice(["Positive", "Negative", "Indeterminate", "Not Tested"])
            }
        }
    })
    
    # 5. Oncotype DX Score (85337-4 with valueQuantity)
    if random.random() > 0.3:  # 70% of patients have this
        observations_to_add.append({
            "fullUrl": f"urn:uuid:oncotype-{patient_num}",
            "resource": {
                "resourceType": "Observation",
                "id": f"oncotype-{patient_num}",
                "status": "final",
                "category": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "laboratory",
                        "display": "Laboratory"
                    }]
                }],
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "85337-4",
                        "display": "Oncotype DX Recurrence Score"
                    }],
                    "text": "Oncotype DX Score"
                },
                "subject": {
                    "reference": f"Patient/{patient_id}"
                },
                "effectiveDateTime": random_date(),
                "valueQuantity": {
                    "value": random.randint(0, 100),
                    "unit": "score"
                }
            }
        })
    
    # 6. Androgen Receptor Status (16112-5)
    observations_to_add.append({
        "fullUrl": f"urn:uuid:androgen-receptor-{patient_num}",
        "resource": {
            "resourceType": "Observation",
            "id": f"androgen-receptor-{patient_num}",
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory",
                    "display": "Laboratory"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "16112-5",
                    "display": "Androgen Receptor"
                }],
                "text": "Androgen Receptor Status"
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": random_date(),
            "valueCodeableConcept": {
                "coding": [{
                    "code": random.choice(["positive", "negative"]),
                    "display": random.choice(["Positive", "Negative"])
                }],
                "text": random.choice(["Positive", "Negative"])
            }
        }
    })
    
    # 7. Therapy Intent (42804-5)
    observations_to_add.append({
        "fullUrl": f"urn:uuid:therapy-intent-{patient_num}",
        "resource": {
            "resourceType": "Observation",
            "id": f"therapy-intent-{patient_num}",
            "status": "final",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "42804-5",
                    "display": "Therapy Intent"
                }],
                "text": "Therapy Intent"
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": random_date(),
            "valueCodeableConcept": {
                "coding": [{
                    "code": random.choice(["adjuvant", "neoadjuvant", "metastatic"]),
                    "display": random.choice(["Adjuvant", "Neoadjuvant", "Metastatic"])
                }],
                "text": random.choice(["Adjuvant", "Neoadjuvant", "Metastatic"])
            }
        }
    })
    
    # 8. Reason for Discontinuation (91379-3) - only for some patients
    if random.random() > 0.6:  # 40% discontinued
        observations_to_add.append({
            "fullUrl": f"urn:uuid:discontinuation-{patient_num}",
            "resource": {
                "resourceType": "Observation",
                "id": f"discontinuation-{patient_num}",
                "status": "final",
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "91379-3",
                        "display": "Reason for Discontinuation"
                    }],
                    "text": "Reason for Discontinuation"
                },
                "subject": {
                    "reference": f"Patient/{patient_id}"
                },
                "effectiveDateTime": random_date(),
                "valueCodeableConcept": {
                    "coding": [{
                        "code": random.choice(["progression", "toxicity", "completion"]),
                        "display": random.choice(["Disease Progression", "Treatment Toxicity", "Treatment Completion"])
                    }],
                    "text": random.choice(["Progression", "Toxicity", "Completion"])
                }
            }
        })
    
    # 9. Magnesium (2601-3)
    observations_to_add.append({
        "fullUrl": f"urn:uuid:magnesium-{patient_num}",
        "resource": {
            "resourceType": "Observation",
            "id": f"magnesium-{patient_num}",
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory",
                    "display": "Laboratory"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "2601-3",
                    "display": "Magnesium"
                }],
                "text": "Magnesium"
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": random_date(),
            "valueQuantity": {
                "value": round(random.uniform(1.7, 2.4), 1),
                "unit": "mg/dL",
                "system": "http://unitsofmeasure.org",
                "code": "mg/dL"
            }
        }
    })
    
    # 10. Phosphorus (2777-1)
    observations_to_add.append({
        "fullUrl": f"urn:uuid:phosphorus-{patient_num}",
        "resource": {
            "resourceType": "Observation",
            "id": f"phosphorus-{patient_num}",
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory",
                    "display": "Laboratory"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "2777-1",
                    "display": "Phosphorus"
                }],
                "text": "Phosphorus"
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": random_date(),
            "valueQuantity": {
                "value": round(random.uniform(2.5, 4.5), 1),
                "unit": "mg/dL",
                "system": "http://unitsofmeasure.org",
                "code": "mg/dL"
            }
        }
    })
    
    # 11 & 12. Pregnancy Test (2106-3) - only for female patients
    if patient_num % 2 == 0:  # Assume half are female
        observations_to_add.append({
            "fullUrl": f"urn:uuid:pregnancy-test-{patient_num}",
            "resource": {
                "resourceType": "Observation",
                "id": f"pregnancy-test-{patient_num}",
                "status": "final",
                "category": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "laboratory",
                        "display": "Laboratory"
                    }]
                }],
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "2106-3",
                        "display": "Pregnancy Test"
                    }],
                    "text": "Pregnancy Test"
                },
                "subject": {
                    "reference": f"Patient/{patient_id}"
                },
                "effectiveDateTime": random_date(),
                "valueCodeableConcept": {
                    "coding": [{
                        "code": random.choice(["negative", "positive"]),
                        "display": random.choice(["Negative", "Positive"])
                    }],
                    "text": random.choice(["Negative", "Positive"])
                }
            }
        })

print(f"Generated {len(observations_to_add)} new observations")

# Add new observations to bundle
bundle['entry'].extend(observations_to_add)

# Update total count
bundle['total'] = len(bundle['entry'])

# Save updated bundle
with open('data/sample_patients_with_blood_counts.json', 'w') as f:
    json.dump(bundle, f, indent=2)

print(f"Updated bundle now has {bundle['total']} total resources")
print("Sample data file updated successfully!")

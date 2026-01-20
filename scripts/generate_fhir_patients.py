"""
Generate FHIR Bundle JSON file from synthetic breast cancer patient data
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Set random seed for reproducibility
random.seed(42)

def generate_random_date(start_year=1950, end_year=2005):
    """Generate a random birth date"""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)

def generate_diagnosis_date(birth_date):
    """Generate a diagnosis date after birth date"""
    today = datetime.now()
    # Diagnosis between age 30 and current age
    min_diagnosis = birth_date + timedelta(days=30*365)
    max_diagnosis = min(today, birth_date + timedelta(days=80*365))
    
    if min_diagnosis >= max_diagnosis:
        return today - timedelta(days=random.randint(365, 3650))
    
    time_between = max_diagnosis - min_diagnosis
    days_between = time_between.days
    if days_between <= 0:
        return today - timedelta(days=random.randint(365, 3650))
    
    random_days = random.randrange(days_between)
    return min_diagnosis + timedelta(days=random_days)

def generate_patient_resource(patient_id, first_name, last_name):
    """Generate a FHIR Patient resource"""
    birth_date = generate_random_date()
    gender = "female"  # Breast cancer primarily affects women
    
    # Generate phone number
    phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    patient = {
        "resourceType": "Patient",
        "id": f"patient-{patient_id}",
        "identifier": [
            {
                "system": "http://hospital.example.org/patients",
                "value": f"MRN-{patient_id:06d}"
            }
        ],
        "active": True,
        "name": [
            {
                "use": "official",
                "family": last_name,
                "given": [first_name]
            }
        ],
        "telecom": [
            {
                "system": "phone",
                "value": phone,
                "use": "mobile"
            }
        ],
        "gender": gender,
        "birthDate": birth_date.strftime("%Y-%m-%d")
    }
    
    return patient, birth_date

def generate_condition_resource(patient_id, birth_date):
    """Generate a FHIR Condition resource for breast cancer diagnosis"""
    
    # Breast cancer histologic types
    histologic_types = [
        {
            "code": "408643008",
            "display": "Invasive ductal carcinoma",
            "system": "http://snomed.info/sct",
            "type": "Invasive Ductal Carcinoma"
        },
        {
            "code": "399294002",
            "display": "Invasive lobular carcinoma of breast",
            "system": "http://snomed.info/sct",
            "type": "Invasive Lobular Carcinoma"
        },
        {
            "code": "254838004",
            "display": "Infiltrating duct carcinoma of breast",
            "system": "http://snomed.info/sct",
            "type": "Infiltrating Ductal Carcinoma"
        },
        {
            "code": "420588008",
            "display": "Tubular carcinoma of breast",
            "system": "http://snomed.info/sct",
            "type": "Tubular Carcinoma"
        },
        {
            "code": "87737001",
            "display": "Medullary carcinoma of breast",
            "system": "http://snomed.info/sct",
            "type": "Medullary Carcinoma"
        },
        {
            "code": "40275004",
            "display": "Mucinous adenocarcinoma of breast",
            "system": "http://snomed.info/sct",
            "type": "Mucinous Carcinoma"
        },
        {
            "code": "733534004",
            "display": "Papillary carcinoma of breast",
            "system": "http://snomed.info/sct",
            "type": "Papillary Carcinoma"
        },
        {
            "code": "1187332001",
            "display": "Triple negative breast cancer",
            "system": "http://snomed.info/sct",
            "type": "Triple Negative Breast Cancer"
        }
    ]
    
    # Weight toward more common types
    weights = [40, 20, 15, 8, 7, 5, 3, 2]  # IDC is most common
    histologic = random.choices(histologic_types, weights=weights)[0]
    diagnosis_date = generate_diagnosis_date(birth_date)
    
    # Clinical staging for breast cancer (TNM-based)
    stages = ["I", "IA", "IB", "II", "IIA", "IIB", "III", "IIIA", "IIIB", "IIIC", "IV"]
    stage_weights = [10, 15, 10, 15, 15, 10, 8, 5, 4, 3, 5]  # Earlier stages more common
    stage = random.choices(stages, weights=stage_weights)[0]
    
    condition = {
        "resourceType": "Condition",
        "id": f"condition-{patient_id}",
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active",
                    "display": "Active"
                }
            ]
        },
        "verificationStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    "code": "confirmed",
                    "display": "Confirmed"
                }
            ]
        },
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                        "code": "encounter-diagnosis",
                        "display": "Encounter Diagnosis"
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": histologic["system"],
                    "code": histologic["code"],
                    "display": histologic["display"]
                }
            ],
            "text": histologic["type"]
        },
        "subject": {
            "reference": f"Patient/patient-{patient_id}"
        },
        "onsetDateTime": diagnosis_date.strftime("%Y-%m-%d"),
        "stage": [
            {
                "summary": {
                    "coding": [
                        {
                            "system": "http://cancerstaging.org",
                            "code": stage,
                            "display": f"Stage {stage}"
                        }
                    ],
                    "text": f"Breast Cancer Stage {stage}"
                },
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-stage-type",
                            "code": "clinical",
                            "display": "Clinical"
                        }
                    ]
                }
            }
        ],
        "note": [
            {
                "text": f"Histologic type: {histologic['type']}"
            }
        ]
    }
    
    return condition, histologic["type"], stage

def generate_observation_resource(patient_id, observation_type, value, unit, date, reference_range=None):
    """Generate a FHIR Observation resource for lab values"""
    
    observation_codes = {
        "hemoglobin": {
            "code": "718-7",
            "display": "Hemoglobin [Mass/volume] in Blood",
            "system": "http://loinc.org"
        },
        "wbc": {
            "code": "6690-2",
            "display": "Leukocytes [#/volume] in Blood",
            "system": "http://loinc.org"
        },
        "anc": {
            "code": "751-8",
            "display": "Neutrophils [#/volume] in Blood",
            "system": "http://loinc.org"
        },
        "platelets": {
            "code": "777-3",
            "display": "Platelets [#/volume] in Blood",
            "system": "http://loinc.org"
        },
        "creatinine": {
            "code": "2160-0",
            "display": "Creatinine [Mass/volume] in Serum or Plasma",
            "system": "http://loinc.org"
        },
        "alt": {
            "code": "1742-6",
            "display": "Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma",
            "system": "http://loinc.org"
        },
        "ast": {
            "code": "1920-8",
            "display": "Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma",
            "system": "http://loinc.org"
        },
        "bilirubin": {
            "code": "1975-2",
            "display": "Bilirubin.total [Mass/volume] in Serum or Plasma",
            "system": "http://loinc.org"
        },
        "albumin": {
            "code": "1751-7",
            "display": "Albumin [Mass/volume] in Serum or Plasma",
            "system": "http://loinc.org"
        },
        "her2": {
            "code": "48676-1",
            "display": "HER2 [Interpretation] in Tissue",
            "system": "http://loinc.org"
        },
        "er": {
            "code": "16112-5",
            "display": "Estrogen receptor [Interpretation] in Tissue",
            "system": "http://loinc.org"
        },
        "pr": {
            "code": "16113-3",
            "display": "Progesterone receptor [Interpretation] in Tissue",
            "system": "http://loinc.org"
        }
    }
    
    code_info = observation_codes.get(observation_type, {"code": "unknown", "display": "Unknown", "system": "http://loinc.org"})
    
    observation = {
        "resourceType": "Observation",
        "id": f"obs-{patient_id}-{observation_type}",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "laboratory",
                        "display": "Laboratory"
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": code_info["system"],
                    "code": code_info["code"],
                    "display": code_info["display"]
                }
            ]
        },
        "subject": {
            "reference": f"Patient/patient-{patient_id}"
        },
        "effectiveDateTime": date.strftime("%Y-%m-%d"),
        "valueQuantity": {
            "value": value,
            "unit": unit,
            "system": "http://unitsofmeasure.org",
            "code": unit
        }
    }
    
    if reference_range:
        observation["referenceRange"] = [{
            "low": {
                "value": reference_range[0],
                "unit": unit
            },
            "high": {
                "value": reference_range[1],
                "unit": unit
            }
        }]
    
    return observation

def generate_biomarker_observation(patient_id, marker_type, date):
    """Generate biomarker observations (HER2, ER, PR)"""
    
    biomarker_codes = {
        "her2": {
            "code": "48676-1",
            "display": "HER2 [Interpretation] in Tissue",
            "values": ["Positive", "Negative", "Equivocal"],
            "weights": [20, 65, 15]
        },
        "er": {
            "code": "16112-5",
            "display": "Estrogen receptor [Interpretation] in Tissue",
            "values": ["Positive", "Negative"],
            "weights": [70, 30]
        },
        "pr": {
            "code": "16113-3",
            "display": "Progesterone receptor [Interpretation] in Tissue",
            "values": ["Positive", "Negative"],
            "weights": [65, 35]
        }
    }
    
    marker = biomarker_codes[marker_type]
    result = random.choices(marker["values"], weights=marker["weights"])[0]
    
    observation = {
        "resourceType": "Observation",
        "id": f"obs-{patient_id}-{marker_type}",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "laboratory",
                        "display": "Laboratory"
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": marker["code"],
                    "display": marker["display"]
                }
            ]
        },
        "subject": {
            "reference": f"Patient/patient-{patient_id}"
        },
        "effectiveDateTime": date.strftime("%Y-%m-%d"),
        "valueCodeableConcept": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "10828004" if result == "Positive" else "260385009",
                    "display": result
                }
            ],
            "text": result
        }
    }
    
    return observation

def generate_fhir_bundle():
    """Generate a complete FHIR Bundle with synthetic breast cancer patients"""
    
    # Sample names
    first_names = [
        "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Mia", "Charlotte", "Amelia",
        "Harper", "Evelyn", "Abigail", "Emily", "Elizabeth", "Sofia", "Avery", "Ella",
        "Scarlett", "Grace", "Chloe", "Victoria", "Riley", "Aria", "Lily", "Aubrey",
        "Zoey", "Penelope", "Lillian", "Addison", "Layla", "Natalie", "Camila", "Hannah",
        "Brooklyn", "Zoe", "Nora", "Leah", "Savannah", "Audrey", "Claire", "Eleanor",
        "Skylar", "Ellie", "Samantha", "Stella", "Paisley", "Violet", "Mila", "Allison",
        "Alexa", "Anna"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White",
        "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"
    ]
    
    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": []
    }
    
    # Generate 50 patients
    num_patients = 50
    
    for i in range(1, num_patients + 1):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Generate patient
        patient, birth_date = generate_patient_resource(i, first_name, last_name)
        bundle["entry"].append({
            "fullUrl": f"http://example.org/Patient/patient-{i}",
            "resource": patient
        })
        
        # Generate condition (diagnosis) with histologic type and stage
        condition, histologic_type, stage = generate_condition_resource(i, birth_date)
        bundle["entry"].append({
            "fullUrl": f"http://example.org/Condition/condition-{i}",
            "resource": condition
        })
        
        # Generate lab observations (recent labs)
        lab_date = datetime.now() - timedelta(days=random.randint(1, 30))
        
        # Hemoglobin (eligibility usually requires >9-10 g/dL)
        hemoglobin = round(random.uniform(9.5, 15.0), 1)
        obs_hgb = generate_observation_resource(i, "hemoglobin", hemoglobin, "g/dL", lab_date, (12.0, 16.0))
        bundle["entry"].append({
            "fullUrl": f"http://example.org/Observation/obs-{i}-hemoglobin",
            "resource": obs_hgb
        })
        
        # WBC (eligibility usually requires >3.0-4.0)
        wbc = round(random.uniform(3.5, 11.0), 1)
        obs_wbc = generate_observation_resource(i, "wbc", wbc, "10*3/uL", lab_date, (4.0, 11.0))
        bundle["entry"].append({
            "fullUrl": f"http://example.org/Observation/obs-{i}-wbc",
            "resource": obs_wbc
        })
        
        # ANC (Absolute Neutrophil Count - eligibility usually requires >1.5)
        anc = round(random.uniform(1.5, 7.0), 1)
        obs_anc = generate_observation_resource(i, "anc", anc, "10*3/uL", lab_date, (1.5, 8.0))
        bundle["entry"].append({
            "fullUrl": f"http://example.org/Observation/obs-{i}-anc",
            "resource": obs_anc
        })
        
        # Platelets (eligibility usually requires >100)
        platelets = random.randint(100, 400)
        obs_platelets = generate_observation_resource(i, "platelets", platelets, "10*3/uL", lab_date, (150, 400))
        bundle["entry"].append({
            "fullUrl": f"http://example.org/Observation/obs-{i}-platelets",
            "resource": obs_platelets
        })
        
        # Creatinine (eligibility usually requires <1.5-2.0 mg/dL)
        creatinine = round(random.uniform(0.6, 1.8), 2)
        obs_creatinine = generate_observation_resource(i, "creatinine", creatinine, "mg/dL", lab_date, (0.6, 1.2))
        bundle["entry"].append({
            "fullUrl": f"http://example.org/Observation/obs-{i}-creatinine",
            "resource": obs_creatinine
        })
        
        # ALT (eligibility usually requires <3x ULN, ~120 U/L)
        alt = random.randint(10, 100)
        obs_alt = generate_observation_resource(i, "alt", alt, "U/L", lab_date, (7, 56))
        bundle["entry"].append({
            "fullUrl": f"http://example.org/Observation/obs-{i}-alt",
            "resource": obs_alt
        })
        
        # AST (eligibility usually requires <3x ULN, ~120 U/L)
        ast = random.randint(10, 100)
        obs_ast = generate_observation_resource(i, "ast", ast, "U/L", lab_date, (8, 48))
        bundle["entry"].append({
            "fullUrl": f"http://example.org/Observation/obs-{i}-ast",
            "resource": obs_ast
        })
        
        # Total Bilirubin (eligibility usually requires <1.5-2x ULN)
        bilirubin = round(random.uniform(0.2, 2.0), 1)
        obs_bilirubin = generate_observation_resource(i, "bilirubin", bilirubin, "mg/dL", lab_date, (0.1, 1.2))
        bundle["entry"].append({
            "fullUrl": f"http://example.org/Observation/obs-{i}-bilirubin",
            "resource": obs_bilirubin
        })
        
        # Albumin (eligibility may require >2.5-3.0 g/dL)
        albumin = round(random.uniform(3.0, 5.0), 1)
        obs_albumin = generate_observation_resource(i, "albumin", albumin, "g/dL", lab_date, (3.5, 5.5))
        bundle["entry"].append({
            "fullUrl": f"http://example.org/Observation/obs-{i}-albumin",
            "resource": obs_albumin
        })
        
        # Biomarkers (HER2, ER, PR)
        biomarker_date = condition["onsetDateTime"]
        
        obs_her2 = generate_biomarker_observation(i, "her2", datetime.strptime(biomarker_date, "%Y-%m-%d"))
        bundle["entry"].append({
            "fullUrl": f"http://example.org/Observation/obs-{i}-her2",
            "resource": obs_her2
        })
        
        obs_er = generate_biomarker_observation(i, "er", datetime.strptime(biomarker_date, "%Y-%m-%d"))
        bundle["entry"].append({
            "fullUrl": f"http://example.org/Observation/obs-{i}-er",
            "resource": obs_er
        })
        
        obs_pr = generate_biomarker_observation(i, "pr", datetime.strptime(biomarker_date, "%Y-%m-%d"))
        bundle["entry"].append({
            "fullUrl": f"http://example.org/Observation/obs-{i}-pr",
            "resource": obs_pr
        })
    
    return bundle

def main():
    """Generate and save FHIR bundle"""
    print("Generating FHIR Bundle with synthetic breast cancer patients...")
    
    bundle = generate_fhir_bundle()
    
    # Save to file
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "synthetic_patients_fhir.json"
    
    with open(output_file, 'w') as f:
        json.dump(bundle, f, indent=2)
    
    print(f"✓ Generated FHIR Bundle with {len([e for e in bundle['entry'] if e['resource']['resourceType'] == 'Patient'])} patients")
    print(f"✓ Saved to: {output_file}")
    print(f"✓ Total resources: {len(bundle['entry'])}")
    print(f"✓ Each patient includes:")
    print(f"  - Breast cancer diagnosis with histologic type and clinical stage")
    print(f"  - Complete blood count (Hemoglobin, WBC, ANC, Platelets)")
    print(f"  - Liver function tests (ALT, AST, Bilirubin)")
    print(f"  - Kidney function (Creatinine)")
    print(f"  - Other labs (Albumin)")
    print(f"  - Biomarkers (HER2, ER, PR status)")

if __name__ == "__main__":
    main()
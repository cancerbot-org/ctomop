#!/usr/bin/env python3
"""
Generate sample data for Coagulation, Tumor Markers, and Behavior tab fields
"""
import json
import random
from datetime import datetime, timedelta

def generate_observation(patient_id, loinc_code, display_text, value, unit, observation_date):
    """Generate a FHIR observation"""
    return {
        "resourceType": "Observation",
        "id": f"obs-{patient_id}-{loinc_code}-{random.randint(1000, 9999)}",
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
                "code": loinc_code,
                "display": display_text
            }],
            "text": display_text
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": observation_date,
        "valueQuantity": {
            "value": value,
            "unit": unit,
            "system": "http://unitsofmeasure.org"
        }
    }

def generate_codeable_observation(patient_id, loinc_code, display_text, value_text, observation_date):
    """Generate a FHIR observation with codeable concept value"""
    return {
        "resourceType": "Observation",
        "id": f"obs-{patient_id}-{loinc_code}-{random.randint(1000, 9999)}",
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "social-history",
                "display": "Social History"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": loinc_code,
                "display": display_text
            }],
            "text": display_text
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": observation_date,
        "valueCodeableConcept": {
            "text": value_text
        }
    }

def main():
    # Load existing FHIR bundle
    with open('data/sample_patients_with_blood_counts.json', 'r') as f:
        bundle = json.load(f)
    
    # Get all patient IDs
    patient_ids = []
    for entry in bundle['entry']:
        if entry['resource']['resourceType'] == 'Patient':
            patient_ids.append(entry['resource']['id'])
    
    print(f"Found {len(patient_ids)} patients")
    
    new_observations = []
    
    for patient_id in patient_ids:
        # Use recent date for observations
        obs_date = (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        
        # === COAGULATION MARKERS ===
        # INR (LOINC 6301-6): Normal range 0.8-1.2
        inr_value = round(random.uniform(0.8, 1.3), 2)
        new_observations.append(generate_observation(
            patient_id, "6301-6", "INR", inr_value, "{INR}", obs_date
        ))
        
        # Prothrombin Time (PT) (LOINC 5902-2): Normal range 11-13.5 seconds
        pt_value = round(random.uniform(11.0, 14.5), 1)
        new_observations.append(generate_observation(
            patient_id, "5902-2", "Prothrombin time", pt_value, "s", obs_date
        ))
        
        # Activated Partial Thromboplastin Time (PTT) (LOINC 3173-2): Normal range 25-35 seconds
        ptt_value = round(random.uniform(25.0, 37.0), 1)
        new_observations.append(generate_observation(
            patient_id, "3173-2", "Activated partial thromboplastin time", ptt_value, "s", obs_date
        ))
        
        # === TUMOR MARKERS ===
        # CEA (LOINC 2039-6): Normal range <5 ng/mL
        cea_value = round(random.uniform(0.5, 8.0), 1)
        new_observations.append(generate_observation(
            patient_id, "2039-6", "Carcinoembryonic antigen", cea_value, "ng/mL", obs_date
        ))
        
        # CA 19-9 (LOINC 25390-6): Normal range <37 U/mL
        ca19_9_value = round(random.uniform(5.0, 50.0), 1)
        new_observations.append(generate_observation(
            patient_id, "25390-6", "Cancer antigen 19-9", ca19_9_value, "U/mL", obs_date
        ))
        
        # PSA (LOINC 2857-1): Normal range <4 ng/mL
        psa_value = round(random.uniform(0.5, 5.5), 2)
        new_observations.append(generate_observation(
            patient_id, "2857-1", "Prostate specific antigen", psa_value, "ng/mL", obs_date
        ))
        
        # === BEHAVIOR TAB - LIFESTYLE FACTORS ===
        # Smoking Status (LOINC 72166-2)
        smoking_statuses = ["Never smoker", "Former smoker", "Current smoker"]
        smoking_status = random.choice(smoking_statuses)
        new_observations.append(generate_codeable_observation(
            patient_id, "72166-2", "Tobacco smoking status", smoking_status, obs_date
        ))
        
        # Pack Years (if former/current smoker) (LOINC 63640-7)
        if smoking_status in ["Former smoker", "Current smoker"]:
            pack_years = round(random.uniform(0.5, 30.0), 1)
            new_observations.append(generate_observation(
                patient_id, "63640-7", "Pack years", pack_years, "{pack years}", obs_date
            ))
        
        # Alcohol Use (LOINC 74013-4)
        alcohol_levels = ["None", "Light", "Moderate", "Heavy"]
        alcohol_use = random.choice(alcohol_levels)
        new_observations.append(generate_codeable_observation(
            patient_id, "74013-4", "Alcohol use", alcohol_use, obs_date
        ))
        
        # Drinks per Week (if not None) (LOINC 11286-7)
        if alcohol_use != "None":
            drinks_per_week = random.randint(1, 14)
            new_observations.append(generate_observation(
                patient_id, "11286-7", "Drinks per week", drinks_per_week, "{drinks}/wk", obs_date
            ))
        
        # Exercise Frequency (LOINC 68516-4)
        exercise_frequencies = ["Never", "Rarely", "1-2 times/week", "3-4 times/week", "5+ times/week"]
        exercise_freq = random.choice(exercise_frequencies)
        new_observations.append(generate_codeable_observation(
            patient_id, "68516-4", "Exercise frequency", exercise_freq, obs_date
        ))
        
        # Exercise Minutes per Week (LOINC 89555-7)
        exercise_minutes = random.randint(0, 300)
        new_observations.append(generate_observation(
            patient_id, "89555-7", "Exercise minutes per week", exercise_minutes, "min/wk", obs_date
        ))
        
        # Diet Type (LOINC 88365-2)
        diet_types = ["Omnivore", "Vegetarian", "Vegan", "Mediterranean", "Low-carb", "Other"]
        diet_type = random.choice(diet_types)
        new_observations.append(generate_codeable_observation(
            patient_id, "88365-2", "Diet type", diet_type, obs_date
        ))
        
        # === BEHAVIOR TAB - SLEEP & WELLBEING ===
        # Sleep Hours per Night (LOINC 93832-4)
        sleep_hours = round(random.uniform(5.0, 9.0), 1)
        new_observations.append(generate_observation(
            patient_id, "93832-4", "Sleep hours per night", sleep_hours, "h", obs_date
        ))
        
        # Sleep Quality (LOINC 93831-6)
        sleep_qualities = ["Poor", "Fair", "Good", "Very Good", "Excellent"]
        sleep_quality = random.choice(sleep_qualities)
        new_observations.append(generate_codeable_observation(
            patient_id, "93831-6", "Sleep quality", sleep_quality, obs_date
        ))
        
        # Stress Level (LOINC 73985-4)
        stress_levels = ["Minimal", "Low", "Moderate", "High", "Very High"]
        stress_level = random.choice(stress_levels)
        new_observations.append(generate_codeable_observation(
            patient_id, "73985-4", "Stress level", stress_level, obs_date
        ))
        
        # Social Support (LOINC 93033-9)
        social_supports = ["None", "Minimal", "Moderate", "Strong", "Very Strong"]
        social_support = random.choice(social_supports)
        new_observations.append(generate_codeable_observation(
            patient_id, "93033-9", "Social support", social_support, obs_date
        ))
        
        # === BEHAVIOR TAB - SOCIOECONOMIC FACTORS ===
        # Employment Status (LOINC 74165-2)
        employment_statuses = ["Employed Full-time", "Employed Part-time", "Unemployed", "Retired", "Student", "Disabled"]
        employment_status = random.choice(employment_statuses)
        new_observations.append(generate_codeable_observation(
            patient_id, "74165-2", "Employment status", employment_status, obs_date
        ))
        
        # Education Level (LOINC 82589-3)
        education_levels = ["Less than High School", "High School Graduate", "Some College", "Associate Degree", "Bachelor's Degree", "Master's Degree", "Doctoral Degree"]
        education_level = random.choice(education_levels)
        new_observations.append(generate_codeable_observation(
            patient_id, "82589-3", "Education level", education_level, obs_date
        ))
        
        # Marital Status (LOINC 45404-1)
        marital_statuses = ["Single", "Married", "Divorced", "Widowed", "Separated", "Domestic Partner"]
        marital_status = random.choice(marital_statuses)
        new_observations.append(generate_codeable_observation(
            patient_id, "45404-1", "Marital status", marital_status, obs_date
        ))
        
        # Insurance Type (LOINC 76513-1)
        insurance_types = ["Private", "Medicare", "Medicaid", "Military", "Uninsured", "Other"]
        insurance_type = random.choice(insurance_types)
        new_observations.append(generate_codeable_observation(
            patient_id, "76513-1", "Insurance type", insurance_type, obs_date
        ))
        
        # Number of Dependents (LOINC 63512-8)
        num_dependents = random.randint(0, 4)
        new_observations.append(generate_observation(
            patient_id, "63512-8", "Number of dependents", num_dependents, "{dependents}", obs_date
        ))
        
        # Annual Household Income (LOINC 77243-3)
        income = random.randint(25000, 150000)
        new_observations.append(generate_observation(
            patient_id, "77243-3", "Annual household income", income, "USD", obs_date
        ))
    
    # Add new observations to bundle
    for obs in new_observations:
        bundle['entry'].append({"resource": obs})
    
    # Save updated bundle
    with open('data/sample_patients_with_blood_counts.json', 'w') as f:
        json.dump(bundle, f, indent=2)
    
    print(f"✓ Added {len(new_observations)} new observations to FHIR bundle")
    print(f"  - 6 coagulation markers per patient (INR, PT, PTT)")
    print(f"  - 6 tumor markers per patient (CEA, CA 19-9, PSA)")
    print(f"  - 16-18 behavior/lifestyle observations per patient")
    print(f"Total resources: {len(bundle['entry'])}")

if __name__ == "__main__":
    main()

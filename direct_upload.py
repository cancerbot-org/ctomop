#!/usr/bin/env python
"""Direct upload script that bypasses the view"""

import os
import django
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from omop_core.models import (
    Person, PatientInfo, Concept, 
    ConditionOccurrence, Measurement, Observation,
    ProcedureOccurrence
)
from django.contrib.auth.models import User

# Load the FHIR bundle
with open('data/test_patients.json', 'r') as f:
    fhir_data = json.load(f)

if fhir_data.get('resourceType') != 'Bundle':
    print("ERROR: FHIR file must be a Bundle")
    exit(1)

created_count = 0
errors = []

# Group resources by patient
patients_data = {}

for entry in fhir_data.get('entry', []):
    resource = entry.get('resource', {})
    resource_type = resource.get('resourceType')
    
    if resource_type == 'Patient':
        patient_id = resource.get('id', '')
        patients_data[patient_id] = {
            'patient': resource,
            'conditions': [],
            'observations': [],
            'medications': []
        }
    elif resource_type == 'Condition':
        patient_ref = resource.get('subject', {}).get('reference', '')
        patient_id = patient_ref.split('/')[-1] if '/' in patient_ref else ''
        if patient_id in patients_data:
            patients_data[patient_id]['conditions'].append(resource)
    elif resource_type == 'Observation':
        patient_ref = resource.get('subject', {}).get('reference', '')
        patient_id = patient_ref.split('/')[-1] if '/' in patient_ref else ''
        if patient_id in patients_data:
            patients_data[patient_id]['observations'].append(resource)
    elif resource_type == 'MedicationStatement':
        patient_ref = resource.get('subject', {}).get('reference', '')
        patient_id = patient_ref.split('/')[-1] if '/' in patient_ref else ''
        if patient_id in patients_data:
            patients_data[patient_id]['medications'].append(resource)

print(f"Found {len(patients_data)} patients to upload")

# Get base IDs
last_person = Person.objects.all().order_by('-person_id').first()
next_person_id = last_person.person_id + 1 if last_person else 1001

# Process each patient
for fhir_patient_id, data in patients_data.items():
    try:
        patient_resource = data['patient']
        
        # Extract patient demographics
        gender = patient_resource.get('gender', 'unknown')
        if gender == 'male':
            gender_concept_id = 8507
        elif gender == 'female':
            gender_concept_id = 8532
        else:
            gender_concept_id = 8551  # Unknown
        
        gender_concept = Concept.objects.filter(concept_id=gender_concept_id).first()
        
        # Extract birth date
        birth_date_str = patient_resource.get('birthDate')
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
        except:
            birth_date = None
        
        # Extract address
        address = patient_resource.get('address', [{}])[0] if patient_resource.get('address') else {}
        city = address.get('city', '')
        region = address.get('state', '')
        postal_code = address.get('postalCode', '')
        country = address.get('country', '')
        
        # Extract ethnicity from extensions
        ethnicity = None
        extensions = patient_resource.get('extension', [])
        for ext in extensions:
            if 'ethnicity' in ext.get('url', '').lower():
                ethnicity = ext.get('valueString', ext.get('valueCodeableConcept', {}).get('text'))
        
        # Extract ECOG from extensions
        ecog = None
        for ext in extensions:
            if 'ecog' in ext.get('url', '').lower():
                ecog_value = ext.get('valueInteger')
                if ecog_value is not None:
                    ecog = ecog_value  # Keep as integer
        
        # Extract vital signs from extensions
        weight = None
        height = None
        systolic_bp = None
        diastolic_bp = None
        heart_rate = None
        
        for ext in extensions:
            url = ext.get('url', '').lower()
            if 'weight' in url or 'bodyweight' in url:
                weight = ext.get('valueQuantity', {}).get('value')
            elif 'height' in url or 'bodyheight' in url:
                height = ext.get('valueQuantity', {}).get('value')
            elif 'systolic' in url:
                systolic_bp = ext.get('valueQuantity', {}).get('value')
            elif 'diastolic' in url:
                diastolic_bp = ext.get('valueQuantity', {}).get('value')
            elif 'heartrate' in url.replace('-', '').replace('_', ''):
                heart_rate = ext.get('valueQuantity', {}).get('value')
        
        # Get race concept (Caucasian/White default)
        race_concept = Concept.objects.filter(concept_id=8527).first()
        
        # Extract name
        name = patient_resource.get('name', [{}])[0] if patient_resource.get('name') else {}
        given_name = ' '.join(name.get('given', [])) if name.get('given') else ''
        family_name = name.get('family', '')
        
        # Create Person with name fields
        person = Person.objects.create(
            person_id=next_person_id,
            gender_concept=gender_concept,
            year_of_birth=birth_date.year if birth_date else None,
            month_of_birth=birth_date.month if birth_date else None,
            day_of_birth=birth_date.day if birth_date else None,
            birth_datetime=birth_date,
            race_concept=race_concept,
            ethnicity_concept=race_concept,
            given_name=given_name,
            family_name=family_name,
        )
        
        # Create User for authentication (optional, not used for display)
        User.objects.create(
            id=person.person_id,
            username=f'patient{person.person_id}',
            first_name=given_name,
            last_name=family_name,
        )
        
        # Extract condition (disease) information
        disease = None
        stage = None
        histologic_type = None
        
        for condition in data['conditions']:
            code = condition.get('code', {})
            code_text = code.get('text', '').lower()
            
            if 'breast' in code_text or 'carcinoma' in code_text or 'neoplasm' in code_text:
                disease = 'Breast Cancer'
                
                # Histologic type is in code.text
                histologic_type = code.get('text', '')
                
                # Extract stage from stage array (not extensions)
                stage_arr = condition.get('stage', [])
                if stage_arr:
                    stage_summary = stage_arr[0].get('summary', {})
                    stage_coding = stage_summary.get('coding', [])
                    if stage_coding:
                        stage = stage_coding[0].get('code', '')
        
        # Extract tumor characteristics and biomarkers from observations
        tumor_size = None
        lymph_node_status = None
        metastasis_status = None
        er_status = None
        pr_status = None
        her2_status = None
        ki67_index = None
        pdl1_percentage = None
        genetic_mutations = []
        
        for observation in data['observations']:
            obs_code = observation.get('code', {})
            obs_text = obs_code.get('text', '').lower()
            
            # Check for tumor size
            if 'tumor size' in obs_text:
                if observation.get('valueQuantity'):
                    tumor_size = observation['valueQuantity'].get('value')
            
            # Check for lymph node status
            elif 'lymph node' in obs_text:
                if observation.get('valueCodeableConcept'):
                    value_concept = observation['valueCodeableConcept']
                    if value_concept.get('text'):
                        lymph_node_status = value_concept['text']
            
            # Check for metastasis status
            elif 'metastasis' in obs_text or 'distant spread' in obs_text:
                if observation.get('valueCodeableConcept'):
                    value_concept = observation['valueCodeableConcept']
                    if value_concept.get('text'):
                        metastasis_status = value_concept['text']
            
            # Check for estrogen receptor
            elif 'estrogen receptor' in obs_text or 'er status' in obs_text:
                if observation.get('valueCodeableConcept'):
                    value_concept = observation['valueCodeableConcept']
                    if value_concept.get('text'):
                        er_status = value_concept['text']
            
            # Check for progesterone receptor
            elif 'progesterone receptor' in obs_text or 'pr status' in obs_text:
                if observation.get('valueCodeableConcept'):
                    value_concept = observation['valueCodeableConcept']
                    if value_concept.get('text'):
                        pr_status = value_concept['text']
            
            # Check for HER2
            elif 'her2' in obs_text or 'her-2' in obs_text:
                if observation.get('valueCodeableConcept'):
                    value_concept = observation['valueCodeableConcept']
                    if value_concept.get('text'):
                        her2_status = value_concept['text']
            
            # Check for Ki-67
            elif 'ki-67' in obs_text or 'ki67' in obs_text:
                if observation.get('valueQuantity'):
                    ki67_index = observation['valueQuantity'].get('value')
            
            # Check for PD-L1
            elif 'pd-l1' in obs_text or 'pdl1' in obs_text:
                if observation.get('component'):
                    for component in observation['component']:
                        comp_text = component.get('code', {}).get('text', '').lower()
                        if 'percentage' in comp_text or 'tumor cells' in comp_text:
                            if component.get('valueQuantity'):
                                pdl1_percentage = component['valueQuantity'].get('value')
            
            # Check for genetic mutations
            elif 'gene' in obs_text and 'mutation' in obs_text:
                mutation_data = {
                    'gene': None,
                    'mutation': None,
                    'origin': None,
                    'interpretation': None
                }
                
                # Get interpretation
                if observation.get('valueCodeableConcept'):
                    value_concept = observation['valueCodeableConcept']
                    if value_concept.get('text'):
                        mutation_data['interpretation'] = value_concept['text']
                
                # Extract from components
                if observation.get('component'):
                    for component in observation['component']:
                        comp_code = component.get('code', {})
                        comp_text = comp_code.get('text', '').lower()
                        
                        if 'gene' in comp_text:
                            if component.get('valueCodeableConcept'):
                                mutation_data['gene'] = component['valueCodeableConcept'].get('text')
                        elif 'mutation' in comp_text or 'dna change' in comp_text:
                            if component.get('valueCodeableConcept'):
                                mutation_data['mutation'] = component['valueCodeableConcept'].get('text')
                        elif 'origin' in comp_text or 'source class' in comp_text:
                            if component.get('valueCodeableConcept'):
                                value = component['valueCodeableConcept'].get('text')
                                if value:
                                    mutation_data['origin'] = value
                
                if mutation_data['gene'] and mutation_data['mutation']:
                    genetic_mutations.append(mutation_data)
        
        # Extract therapy lines from medications
        therapy_lines = {}  # {line_number: {'regimen': name, 'date': date, 'outcome': outcome, 'drugs': []}}
        
        for medication in data['medications']:
            # Get therapy line and outcome from extensions
            line_number = None
            outcome = None
            for ext in medication.get('extension', []):
                if 'therapy-line' in ext.get('url', ''):
                    line_number = ext.get('valueInteger')
                elif 'therapy-outcome' in ext.get('url', ''):
                    outcome = ext.get('valueString')
            
            if line_number is None:
                continue
            
            # Check if this is a regimen (has no partOf) or individual drug
            is_regimen = 'partOf' not in medication
            
            if is_regimen:
                # This is the named regimen
                regimen_name = medication.get('medicationCodeableConcept', {}).get('text', '')
                effective_period = medication.get('effectivePeriod', {})
                start_date_str = effective_period.get('start')
                start_date = None
                if start_date_str:
                    try:
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    except:
                        pass
                
                if line_number not in therapy_lines:
                    therapy_lines[line_number] = {
                        'regimen': regimen_name,
                        'date': start_date,
                        'outcome': outcome,
                        'drugs': []
                    }
                else:
                    therapy_lines[line_number]['regimen'] = regimen_name
                    therapy_lines[line_number]['date'] = start_date
                    therapy_lines[line_number]['outcome'] = outcome
            else:
                # This is an individual drug in the regimen
                drug_name = medication.get('medicationCodeableConcept', {}).get('text', '')
                rxnorm_code = None
                coding = medication.get('medicationCodeableConcept', {}).get('coding', [])
                if coding:
                    rxnorm_code = coding[0].get('code')
                
                effective_period = medication.get('effectivePeriod', {})
                start_date_str = effective_period.get('start')
                end_date_str = effective_period.get('end')
                
                start_date = None
                end_date = None
                if start_date_str:
                    try:
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    except:
                        pass
                if end_date_str:
                    try:
                        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    except:
                        pass
                
                if line_number not in therapy_lines:
                    therapy_lines[line_number] = {
                        'regimen': None,
                        'date': start_date.date() if start_date else None,
                        'drugs': []
                    }
                
                therapy_lines[line_number]['drugs'].append({
                    'name': drug_name,
                    'rxnorm': rxnorm_code,
                    'start_date': start_date,
                    'end_date': end_date
                })
        
        # Extract therapy info for PatientInfo
        first_line_therapy = None
        first_line_date = None
        first_line_outcome = None
        second_line_therapy = None
        second_line_date = None
        second_line_outcome = None
        later_therapy = None
        later_date = None
        later_outcome = None
        
        if 1 in therapy_lines:
            first_line_therapy = therapy_lines[1]['regimen']
            first_line_date = therapy_lines[1]['date']
            first_line_outcome = therapy_lines[1].get('outcome')
        if 2 in therapy_lines:
            second_line_therapy = therapy_lines[2]['regimen']
            second_line_date = therapy_lines[2]['date']
            second_line_outcome = therapy_lines[2].get('outcome')
        # Map line 3 and 4 to "later" field (prioritize most recent)
        if 4 in therapy_lines:
            later_therapy = therapy_lines[4]['regimen']
            later_date = therapy_lines[4]['date']
            later_outcome = therapy_lines[4].get('outcome')
        elif 3 in therapy_lines:
            later_therapy = therapy_lines[3]['regimen']
            later_date = therapy_lines[3]['date']
            later_outcome = therapy_lines[3].get('outcome')
        
        # Create PatientInfo
        patient_info = PatientInfo.objects.create(
            person=person,
            date_of_birth=birth_date,
            disease=disease,
            stage=stage,
            histologic_type=histologic_type,
            country=country,
            region=region,
            city=city,
            postal_code=postal_code,
            ethnicity=ethnicity,
            weight=weight,
            weight_units='kg' if weight else None,
            height=height,
            height_units='cm' if height else None,
            systolic_blood_pressure=systolic_bp,
            diastolic_blood_pressure=diastolic_bp,
            heartrate=heart_rate,
            ecog_performance_status=ecog,
            tumor_size=tumor_size,
            lymph_node_status=lymph_node_status,
            metastasis_status=metastasis_status,
            estrogen_receptor_status=er_status,
            progesterone_receptor_status=pr_status,
            her2_status=her2_status,
            ki67_proliferation_index=ki67_index,
            pd_l1_tumor_cels=pdl1_percentage,
            genetic_mutations=genetic_mutations,
            first_line_therapy=first_line_therapy,
            first_line_date=first_line_date,
            first_line_outcome=first_line_outcome,
            second_line_therapy=second_line_therapy,
            second_line_date=second_line_date,
            second_line_outcome=second_line_outcome,
            later_therapy=later_therapy,
            later_date=later_date,
            later_outcome=later_outcome,
        )
        
        # TODO: Create DrugExposure records - skipping for now due to schema mismatch
        # Will add after verifying database column names
        
        num_lines = len(therapy_lines)
        created_count += 1
        next_person_id += 1
        print(f"✓ Created patient {person.person_id} ({given_name} {family_name}) - {len(genetic_mutations)} mutation(s), {num_lines} therapy line(s)")
        
    except Exception as e:
        errors.append(f"Patient {fhir_patient_id}: {str(e)}")
        print(f"✗ Error with patient {fhir_patient_id}: {str(e)}")

print(f"\n{'='*60}")
print(f"Upload complete: {created_count} patients created")
if errors:
    print(f"Errors: {len(errors)}")
    for err in errors:
        print(f"  - {err}")

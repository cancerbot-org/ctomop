"""
Django management command to populate PatientInfo from OMOP and extension models.

This command reads data from all OMOP CDM tables and extension models
to populate comprehensive PatientInfo records for clinical trial matching.

Usage:
    python manage.py populate_patient_info
    python manage.py populate_patient_info --person-id 4001
    python manage.py populate_patient_info --force-update --verbose
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from datetime import date, datetime, timedelta
import json
from omop_core.models import (
    Person, PatientInfo, ConditionOccurrence, Concept,
    Measurement, Observation, DrugExposure, Location
)
# Extension models have been removed for OMOP compliance
# All data is now extracted from standard OMOP tables


class Command(BaseCommand):
    help = 'Populate PatientInfo from OMOP and extension models for all persons'

    def add_arguments(self, parser):
        parser.add_argument(
            '--person-id',
            type=int,
            help='Process specific person ID only',
        )
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Force update existing PatientInfo records',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed processing information',
        )

    def handle(self, *args, **options):
        person_id = options.get('person_id')
        force_update = options.get('force_update')
        verbose = options.get('verbose')

        if person_id:
            persons = Person.objects.filter(person_id=person_id)
            if not persons.exists():
                self.stdout.write(
                    self.style.ERROR(f'Person with ID {person_id} not found')
                )
                return
        else:
            persons = Person.objects.all()

        total_persons = persons.count()
        processed_count = 0
        created_count = 0
        updated_count = 0
        skipped_count = 0

        self.stdout.write(f'Processing {total_persons} person(s)...')

        for person in persons:
            try:
                with transaction.atomic():
                    result = self.process_person(person, force_update, verbose)
                    if result == 'created':
                        created_count += 1
                    elif result == 'updated':
                        updated_count += 1
                    elif result == 'skipped':
                        skipped_count += 1
                    
                    processed_count += 1
                    
                    if verbose:
                        self.stdout.write(f'  Person {person.person_id}: {result}')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing Person {person.person_id}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Processing complete:\n'
                f'  Total processed: {processed_count}\n'
                f'  Created: {created_count}\n'
                f'  Updated: {updated_count}\n'
                f'  Skipped: {skipped_count}'
            )
        )

    def process_person(self, person, force_update, verbose):
        """Process a single person and populate their PatientInfo"""
        
        # Check if PatientInfo already exists
        try:
            patient_info = PatientInfo.objects.get(person=person)
            if not force_update:
                return 'skipped'
            action = 'updated'
        except PatientInfo.DoesNotExist:
            patient_info = PatientInfo(person=person)
            action = 'created'

        # Populate demographics from Person
        demographics = self.get_demographics(person)
        for field, value in demographics.items():
            setattr(patient_info, field, value)

        # Populate location data
        location_data = self.get_location_data(person)
        for field, value in location_data.items():
            setattr(patient_info, field, value)

        # Populate disease information
        disease_data = self.get_disease_data(person)
        for field, value in disease_data.items():
            setattr(patient_info, field, value)

        # Populate treatment information
        treatment_data = self.get_treatment_data(person)
        for field, value in treatment_data.items():
            setattr(patient_info, field, value)

        # Populate vital signs and measurements
        vitals_data = self.get_vitals_data(person)
        for field, value in vitals_data.items():
            setattr(patient_info, field, value)

        # Populate biomarkers
        biomarker_data = self.get_biomarker_data(person)
        for field, value in biomarker_data.items():
            setattr(patient_info, field, value)

        # Populate social determinants
        social_data = self.get_social_data(person)
        for field, value in social_data.items():
            setattr(patient_info, field, value)

        # Populate health behaviors
        behavior_data = self.get_behavior_data(person)
        for field, value in behavior_data.items():
            setattr(patient_info, field, value)

        # Populate infection status
        infection_data = self.get_infection_data(person)
        for field, value in infection_data.items():
            setattr(patient_info, field, value)

        # Populate tumor assessments
        assessment_data = self.get_assessment_data(person)
        for field, value in assessment_data.items():
            setattr(patient_info, field, value)

        # Populate laboratory results
        lab_data = self.get_laboratory_data(person)
        for field, value in lab_data.items():
            setattr(patient_info, field, value)

        # Populate performance status
        performance_data = self.get_performance_data(person)
        for field, value in performance_data.items():
            setattr(patient_info, field, value)

        # Populate genetic mutations
        genetic_data = self.get_genetic_mutations(person)
        for field, value in genetic_data.items():
            setattr(patient_info, field, value)

        # Set last updated timestamp
        patient_info.last_updated = timezone.now()

        # Save the PatientInfo
        patient_info.save()

        return action

    def get_demographics(self, person):
        """Extract demographic information from Person model"""
        data = {}
        
        # Age calculation
        if person.year_of_birth:
            today = date.today()
            age = today.year - person.year_of_birth
            if today.month < person.month_of_birth or (
                today.month == person.month_of_birth and 
                today.day < (person.day_of_birth or 1)
            ):
                age -= 1
            data['patient_age'] = age

        # Gender mapping
        if person.gender_concept:
            gender_name = person.gender_concept.concept_name.lower()
            if 'male' in gender_name and 'female' not in gender_name:
                data['gender'] = 'M'
            elif 'female' in gender_name:
                data['gender'] = 'F'
            else:
                data['gender'] = 'U'

        # Race and ethnicity
        if person.race_concept:
            data['ethnicity'] = person.race_concept.concept_name

        # Language support (from PersonLanguageSkill model)
        primary_language = person.get_primary_language()
        if primary_language:
            data['languages'] = primary_language
            # Get language skills summary for additional context
            language_skills = person.get_language_skills_summary()
            if language_skills:
                data['language_skill_level'] = list(language_skills.values())[0] if language_skills else 'speak'
            else:
                data['language_skill_level'] = 'speak'

        return data

    def get_location_data(self, person):
        """Extract location information"""
        data = {}
        
        if person.location:
            location = person.location
            data.update({
                'country': location.country,
                'region': location.state,
                'postal_code': location.zip,
                'latitude': float(location.latitude) if location.latitude else None,
                'longitude': float(location.longitude) if location.longitude else None,
            })

        return data

    def get_disease_data(self, person):
        """Extract disease information from ConditionOccurrence"""
        data = {}
        
        # Get primary cancer diagnosis (most recent)
        cancer_condition = ConditionOccurrence.objects.filter(
            person=person,
            condition_concept__concept_name__icontains='cancer'
        ).order_by('-condition_start_date').first()

        if cancer_condition:
            data['disease'] = cancer_condition.condition_concept.concept_name
            # Note: Staging info should be stored in Measurement or Observation tables
            # For now, we'll just capture the basic disease name

        return data

    def get_treatment_data(self, person):
        """Extract treatment information from DrugExposure table"""
        data = {}
        
        # Get drug exposures ordered by start date
        drug_exposures = DrugExposure.objects.filter(person=person).order_by('-drug_exposure_start_date')
        
        if drug_exposures.exists():
            # Get recent treatments 
            recent_drugs = drug_exposures[:10]  # Last 10 drug exposures
            
            # Extract therapy line information from drug exposure patterns
            unique_dates = set(drug.drug_exposure_start_date for drug in drug_exposures)
            data['therapy_lines_count'] = len(unique_dates)
            
            # Current medications from recent drug exposures
            current_meds = []
            for drug in recent_drugs[:5]:  # Top 5 recent drugs
                if drug.drug_concept:
                    current_meds.append(drug.drug_concept.concept_name)
            
            if current_meds:
                data['concomitant_medications'] = ', '.join(current_meds)

            # Treatment history from drug exposures
            therapy_details = []
            for drug in drug_exposures:
                drug_info = {
                    'drug': drug.drug_concept.concept_name if drug.drug_concept else 'Unknown',
                    'start_date': str(drug.drug_exposure_start_date),
                    'end_date': str(drug.drug_exposure_end_date) if drug.drug_exposure_end_date else None,
                }
                therapy_details.append(drug_info)

            # Extract first, second, and later line information from drug patterns
            if len(therapy_details) >= 1:
                first_drug = therapy_details[0]
                data['first_line_therapy'] = first_drug['drug']
                data['first_line_date'] = first_drug['start_date']

            if len(therapy_details) >= 2:
                second_drug = therapy_details[1]
                data['second_line_therapy'] = second_drug['drug']
                data['second_line_date'] = second_drug['start_date']

            if len(therapy_details) > 2:
                later_drugs = therapy_details[2:]
                data['later_therapy'] = '; '.join([drug['drug'] for drug in later_drugs[:3]])
                data['later_date'] = later_drugs[0]['start_date']

            # Treatment types based on drug concepts
            drug_names = [drug.drug_concept.concept_name.lower() if drug.drug_concept else '' 
                         for drug in drug_exposures]
            
            # Look for platinum-based drugs
            platinum_terms = ['platinum', 'carboplatin', 'cisplatin', 'oxaliplatin']
            if any(any(term in name for term in platinum_terms) for name in drug_names):
                data['prior_therapy'] = 'Platinum-based chemotherapy'
                
            # Look for immunotherapy
            immuno_terms = ['pembrolizumab', 'nivolumab', 'atezolizumab', 'durvalumab']
            if any(any(term in name for term in immuno_terms) for name in drug_names):
                existing_therapy = data.get('prior_therapy', '')
                data['prior_therapy'] = (existing_therapy + '; Immunotherapy').strip('; ')

        return data
        
        if drug_exposures.exists():
            # Get recent treatments 
            recent_drugs = drug_exposures[:10]  # Last 10 drug exposures
            
            # Extract therapy line information from drug exposure patterns
            unique_dates = set(drug.drug_exposure_start_date for drug in drug_exposures)
            data['therapy_lines_count'] = len(unique_dates)
            
            # Current medications from recent drug exposures
            current_meds = []
            for drug in recent_drugs[:5]:  # Top 5 recent drugs
                if drug.drug_concept:
                    current_meds.append(drug.drug_concept.concept_name)
            
            if current_meds:
                data['concomitant_medications'] = ', '.join(current_meds)

            # Treatment history from drug exposures
            therapy_details = []
            for drug in drug_exposures:
                drug_info = {
                    'drug': drug.drug_concept.concept_name if drug.drug_concept else 'Unknown',
                    'start_date': str(drug.drug_exposure_start_date),
                    'end_date': str(drug.drug_exposure_end_date) if drug.drug_exposure_end_date else None,
                }
                therapy_details.append(drug_info)

            # Extract first, second, and later line information from drug patterns
            if len(therapy_details) >= 1:
                first_drug = therapy_details[0]
                data['first_line_therapy'] = first_drug['drug']
                data['first_line_date'] = first_drug['start_date']

            if len(therapy_details) >= 2:
                second_drug = therapy_details[1]
                data['second_line_therapy'] = second_drug['drug']
                data['second_line_date'] = second_drug['start_date']

            if len(therapy_details) > 2:
                later_drugs = therapy_details[2:]
                data['later_therapy'] = '; '.join([drug['drug'] for drug in later_drugs[:3]])
                data['later_date'] = later_drugs[0]['start_date']

            # Treatment types based on drug concepts
            drug_names = [drug.drug_concept.concept_name.lower() if drug.drug_concept else '' 
                         for drug in drug_exposures]
            
            # Look for platinum-based drugs
            platinum_terms = ['platinum', 'carboplatin', 'cisplatin', 'oxaliplatin']
            if any(any(term in name for term in platinum_terms) for name in drug_names):
                data['prior_therapy'] = 'Platinum-based chemotherapy'
                
            # Look for immunotherapy
            immuno_terms = ['pembrolizumab', 'nivolumab', 'atezolizumab', 'durvalumab']
            if any(any(term in name for term in immuno_terms) for name in drug_names):
                existing_therapy = data.get('prior_therapy', '')
                data['prior_therapy'] = (existing_therapy + '; Immunotherapy').strip('; ')

        return data

    def get_vitals_data(self, person):
        """Extract vital signs data from standard OMOP Measurement table"""
        data = {}
        
        # Define LOINC concepts for vital signs
        vital_sign_concepts = {
            'systolic_bp': '8480-6',     # Systolic blood pressure
            'diastolic_bp': '8462-4',    # Diastolic blood pressure
            'heart_rate': '8867-4',      # Heart rate
            'weight': '29463-7',         # Body weight
            'height': '8302-2',          # Body height
            'temperature': '8310-5',     # Body temperature
        }
        
        # Get recent measurements for each vital sign type
        for vital_type, loinc_code in vital_sign_concepts.items():
            try:
                # Find concept by LOINC code
                concept = Concept.objects.filter(
                    concept_code=loinc_code,
                    vocabulary__vocabulary_id='LOINC'
                ).first()
                
                if concept:
                    # Get most recent measurement
                    measurement = Measurement.objects.filter(
                        person=person,
                        measurement_concept=concept,
                        value_as_number__isnull=False
                    ).order_by('-measurement_date').first()
                    
                    if measurement:
                        value = float(measurement.value_as_number)
                        
                        # Store values with appropriate field names
                        if vital_type == 'systolic_bp':
                            data['systolic_blood_pressure'] = int(value)
                        elif vital_type == 'diastolic_bp':
                            data['diastolic_blood_pressure'] = int(value)
                        elif vital_type == 'heart_rate':
                            data['heartrate'] = int(value)
                        elif vital_type == 'weight':
                            # Convert to kg if needed based on unit
                            data['weight'] = value
                            data['weight_units'] = 'kg'  # Assuming kg, could check unit_concept
                        elif vital_type == 'height':
                            # Convert to cm if needed based on unit
                            data['height'] = value
                            data['height_units'] = 'cm'  # Assuming cm, could check unit_concept
                        elif vital_type == 'temperature':
                            data['temperature'] = value
                            
            except Exception as e:
                # Skip if concept not found or other error
                continue

        return data

    def get_biomarker_data(self, person):
        """Extract biomarker information from Measurement table using LOINC concepts"""
        data = {}
        
        # Get measurements for this person
        measurements = Measurement.objects.filter(person=person).order_by('-measurement_date')
        
        # PD-L1 measurements (LOINC concept for PD-L1 expression)
        # Using example LOINC codes - these would need to be mapped to actual concepts
        pdl1_measurements = measurements.filter(measurement_concept__concept_code__in=[
            '85337-4',  # PD-L1 expression example LOINC
        ])
        if pdl1_measurements.exists():
            pdl1_test = pdl1_measurements.first()
            data['pd_l1_tumor_cels'] = int(pdl1_test.value_as_number) if pdl1_test.value_as_number else None
            data['pd_l1_assay'] = pdl1_test.value_source_value  # Assay method in source value

        # Estrogen Receptor (ER) - LOINC 16112-5
        er_measurements = measurements.filter(measurement_concept__concept_code='16112-5')
        if er_measurements.exists():
            er_test = er_measurements.first()
            # Map value_as_concept to clinical significance
            if er_test.value_as_concept_id:
                concept = Concept.objects.get(pk=er_test.value_as_concept_id)
                if 'positive' in concept.concept_name.lower():
                    data['estrogen_receptor_status'] = 'POSITIVE'
                elif 'negative' in concept.concept_name.lower():
                    data['estrogen_receptor_status'] = 'NEGATIVE'

        # Progesterone Receptor (PR) - LOINC 16113-3  
        pr_measurements = measurements.filter(measurement_concept__concept_code='16113-3')
        if pr_measurements.exists():
            pr_test = pr_measurements.first()
            if pr_test.value_as_concept_id:
                concept = Concept.objects.get(pk=pr_test.value_as_concept_id)
                if 'positive' in concept.concept_name.lower():
                    data['progesterone_receptor_status'] = 'POSITIVE'
                elif 'negative' in concept.concept_name.lower():
                    data['progesterone_receptor_status'] = 'NEGATIVE'

        # HER2 - LOINC 48676-1
        her2_measurements = measurements.filter(measurement_concept__concept_code='48676-1')
        if her2_measurements.exists():
            her2_test = her2_measurements.first()
            if her2_test.value_as_concept_id:
                concept = Concept.objects.get(pk=her2_test.value_as_concept_id)
                if 'positive' in concept.concept_name.lower():
                    data['her2_status'] = 'POSITIVE'
                elif 'negative' in concept.concept_name.lower():
                    data['her2_status'] = 'NEGATIVE'

        # Triple negative status calculation
        if ('estrogen_receptor_status' in data and 
            'progesterone_receptor_status' in data and 
            'her2_status' in data):
            is_tnbc = (data['estrogen_receptor_status'] == 'NEGATIVE' and 
                      data['progesterone_receptor_status'] == 'NEGATIVE' and 
                      data['her2_status'] == 'NEGATIVE')
            data['tnbc_status'] = is_tnbc

        return data

    def get_social_data(self, person):
        """Extract social determinants from Observation table"""
        data = {}
        
        # Get observations for social determinants using SNOMED/LOINC concepts
        observations = Observation.objects.filter(person=person)
        
        # Employment status observations (example SNOMED concepts)
        employment_obs = observations.filter(observation_concept__concept_code__in=[
            '224362002',  # Employment status
            '160903007',  # Unemployed
        ])
        if employment_obs.exists():
            # Map observation values to employment status
            data['no_pre_existing_conditions'] = employment_obs.first().value_as_string

        # Insurance status observations  
        insurance_obs = observations.filter(observation_concept__concept_code__in=[
            '408729009',  # Insurance status
        ])
        if insurance_obs.exists():
            data['concomitant_medication_details'] = insurance_obs.first().value_as_string

        return data

    def get_behavior_data(self, person):
        """Extract health behaviors from Observation table"""
        data = {}
        
        # Get behavior observations using SNOMED concepts
        observations = Observation.objects.filter(person=person)
        
        # Tobacco use observations (SNOMED concepts)
        tobacco_obs = observations.filter(observation_concept__concept_code__in=[
            '266919005',  # Never smoked tobacco
            '8517006',    # Former smoker
            '77176002',   # Smoker
        ])
        
        for obs in tobacco_obs:
            if obs.observation_concept.concept_code == '266919005':  # Never smoked
                data['no_tobacco_use_status'] = True
                data['tobacco_use_details'] = 'Never smoker'
            elif obs.observation_concept.concept_code == '8517006':  # Former smoker
                data['no_tobacco_use_status'] = False
                data['tobacco_use_details'] = f'Former smoker, quit {obs.observation_date}'
            elif obs.observation_concept.concept_code == '77176002':  # Current smoker
                data['no_tobacco_use_status'] = False
                data['tobacco_use_details'] = 'Current smoker'

        return data

    def get_infection_data(self, person):
        """Extract infection status from Measurement and Observation tables"""
        data = {}
        
        # Get measurements and observations for infectious diseases
        measurements = Measurement.objects.filter(person=person)
        observations = Observation.objects.filter(person=person)
        
        # HIV status (LOINC concepts for HIV tests)
        hiv_measurements = measurements.filter(measurement_concept__concept_code__in=[
            '5221-7',   # HIV 1 Ab
            '7917-8',   # HIV 1+2 Ab
        ])
        for measurement in hiv_measurements:
            if measurement.value_as_concept_id:
                concept = Concept.objects.get(pk=measurement.value_as_concept_id)
                if 'negative' in concept.concept_name.lower():
                    data['no_hiv_status'] = True
                    data['hiv_status'] = False
                elif 'positive' in concept.concept_name.lower():
                    data['no_hiv_status'] = False
                    data['hiv_status'] = True

        # Hepatitis B (LOINC concepts)
        hepb_measurements = measurements.filter(measurement_concept__concept_code__in=[
            '5195-3',   # Hepatitis B surface antigen
        ])
        for measurement in hepb_measurements:
            if measurement.value_as_concept_id:
                concept = Concept.objects.get(pk=measurement.value_as_concept_id)
                if 'negative' in concept.concept_name.lower():
                    data['no_hepatitis_b_status'] = True
                    data['hepatitis_b_status'] = False
                elif 'positive' in concept.concept_name.lower():
                    data['no_hepatitis_b_status'] = False
                    data['hepatitis_b_status'] = True

        # Hepatitis C (LOINC concepts)
        hepc_measurements = measurements.filter(measurement_concept__concept_code__in=[
            '5196-1',   # Hepatitis C Ab
        ])
        for measurement in hepc_measurements:
            if measurement.value_as_concept_id:
                concept = Concept.objects.get(pk=measurement.value_as_concept_id)
                if 'negative' in concept.concept_name.lower():
                    data['no_hepatitis_c_status'] = True
                    data['hepatitis_c_status'] = False
                elif 'positive' in concept.concept_name.lower():
                    data['no_hepatitis_c_status'] = False
                    data['hepatitis_c_status'] = True

        return data

    def get_assessment_data(self, person):
        """Extract tumor assessment data from Observation table"""
        data = {}
        
        # Get tumor response assessments using SNOMED concepts
        observations = Observation.objects.filter(person=person).order_by('-observation_date')
        
        # Response to treatment observations (SNOMED concepts)
        response_obs = observations.filter(observation_concept__concept_code__in=[
            '182840001',  # Complete response
            '182841002',  # Partial response
            '182843004',  # Stable disease
            '182842009',  # Progressive disease
        ])
        
        if response_obs.exists():
            latest_response = response_obs.first()
            
            # Response mapping from SNOMED codes
            response_map = {
                '182840001': 'Complete Response',
                '182841002': 'Partial Response', 
                '182843004': 'Stable Disease',
                '182842009': 'Progressive Disease'
            }
            
            concept_code = latest_response.observation_concept.concept_code
            if concept_code in response_map:
                data['best_response'] = response_map[concept_code]

        # RECIST measurements from Measurement table
        measurements = Measurement.objects.filter(person=person).order_by('-measurement_date')
        
        # Target lesion sum measurements (example LOINC concept)
        lesion_measurements = measurements.filter(measurement_concept__concept_code__in=[
            '33747-0',  # Sum of target lesions example
        ])
        
        if lesion_measurements.exists():
            latest_measurement = lesion_measurements.first()
            if latest_measurement.value_as_number:
                data['measurable_disease_by_recist_status'] = True

        return data

    def get_laboratory_data(self, person):
        """Extract laboratory test results from Measurement"""
        data = {}
        
        measurements = Measurement.objects.filter(person=person).order_by('-measurement_date')
        
        # Common lab mappings
        lab_mappings = {
            'hemoglobin': ['hemoglobin_level', 'G/DL'],
            'platelet': ['platelet_count', 'CELLS/UL'],
            'creatinine': ['serum_creatinine_level', 'MG/DL'],
            'calcium': ['serum_calcium_level', 'MG/DL'],
            'bilirubin': ['serum_bilirubin_level_total', 'MG/DL'],
            'albumin': ['albumin_level', 'G/DL'],
        }
        
        for measurement in measurements:
            concept_name = measurement.measurement_concept.concept_name.lower()
            
            for lab_key, (field_name, unit_field) in lab_mappings.items():
                if lab_key in concept_name and measurement.value_as_number:
                    data[field_name] = measurement.value_as_number
                    # Set corresponding unit field
                    unit_field_name = f"{field_name}_units"
                    data[unit_field_name] = unit_field
                    break

        return data

    def get_performance_data(self, person):
        """Extract performance status from Observation"""
        data = {}
        
        observations = Observation.objects.filter(person=person).order_by('-observation_date')
        
        for obs in observations:
            concept_name = obs.observation_concept.concept_name.lower()
            
            if 'ecog' in concept_name and obs.value_as_number is not None:
                data['ecog_performance_status'] = int(obs.value_as_number)
                break
            elif 'karnofsky' in concept_name and obs.value_as_number is not None:
                data['karnofsky_performance_score'] = int(obs.value_as_number)
                break

        return data

    def get_genetic_mutations(self, person):
        """Extract genetic mutations from standard OMOP Measurement table"""
        data = {}
        
        # LOINC codes for genetic tests
        genetic_loinc_codes = {
            '21636-6': 'BRCA1',    # BRCA1 gene mutation
            '21637-4': 'BRCA2',    # BRCA2 gene mutation  
            '21667-1': 'TP53',     # TP53 gene mutation
            '48013-7': 'KRAS',     # KRAS gene mutation
            '62862-8': 'EGFR',     # EGFR gene mutation
            '62318-1': 'PIK3CA',   # PIK3CA gene mutation
        }
        
        # SNOMED codes for mutation origin
        origin_concepts = {
            255395001: 'germline',
            255461003: 'somatic'
        }
        
        # SNOMED codes for clinical interpretation
        interpretation_concepts = {
            30166007: 'pathogenic',
            10828004: 'benign', 
            42425007: 'vus'  # Variant of Unknown Significance - shortened
        }
        
        mutations = []
        
        # Get all genetic test measurements for this person
        genetic_measurements = Measurement.objects.filter(
            person=person,
            measurement_concept__concept_code__in=genetic_loinc_codes.keys()
        ).order_by('-measurement_date')
        
        for measurement in genetic_measurements:
            # Skip if no result
            if not measurement.value_as_string:
                continue
                
            gene = genetic_loinc_codes.get(measurement.measurement_concept.concept_code)
            if not gene:
                continue
                
            mutation_data = {
                'gene': gene.lower(),  # Lowercase gene name as requested
                'variant': measurement.value_as_string,  # HGVS notation
                'test_date': measurement.measurement_date.isoformat() if measurement.measurement_date else None,
            }
            
            # Add origin (germline/somatic) from qualifier_concept_id
            if measurement.qualifier_concept_id and measurement.qualifier_concept_id in origin_concepts:
                mutation_data['origin'] = origin_concepts[measurement.qualifier_concept_id]
            
            # Add clinical interpretation from value_as_concept_id  
            if measurement.value_as_concept_id and measurement.value_as_concept_id in interpretation_concepts:
                mutation_data['interpretation'] = interpretation_concepts[measurement.value_as_concept_id]
            
            # Add assay method if available in qualifier_source_value
            if measurement.qualifier_source_value:
                mutation_data['assay_method'] = measurement.qualifier_source_value
                
            mutations.append(mutation_data)
        
        # Set the genetic_mutations field
        data['genetic_mutations'] = mutations
        
        return data

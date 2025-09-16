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
    Person, PatientInfo, ConditionOccurrence, VitalSignMeasurement,
    Measurement, Observation, DrugExposure, Location
)
from omop_genomics.models import BiomarkerMeasurement, TumorAssessment
from omop_oncology.models import TreatmentLine, SocialDeterminant, HealthBehavior, InfectionStatus


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

        # Language
        if person.primary_language_concept:
            data['languages'] = person.primary_language_concept.concept_name
            data['language_skill_level'] = person.language_skill_level or 'speak'

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
            
            # Staging information
            if cancer_condition.clinical_stage_group:
                data['stage'] = cancer_condition.clinical_stage_group
            elif cancer_condition.pathologic_stage_group:
                data['stage'] = cancer_condition.pathologic_stage_group

            # TNM staging
            if cancer_condition.tnm_clinical_t or cancer_condition.tnm_pathologic_t:
                data['tumor_stage'] = cancer_condition.tnm_clinical_t or cancer_condition.tnm_pathologic_t
            if cancer_condition.tnm_clinical_n or cancer_condition.tnm_pathologic_n:
                data['nodes_stage'] = cancer_condition.tnm_clinical_n or cancer_condition.tnm_pathologic_n
            if cancer_condition.tnm_clinical_m or cancer_condition.tnm_pathologic_m:
                data['distant_metastasis_stage'] = cancer_condition.tnm_clinical_m or cancer_condition.tnm_pathologic_m

            # Histology
            if cancer_condition.histology_concept:
                data['histologic_type'] = cancer_condition.histology_concept.concept_name

            # Grade
            if cancer_condition.grade_concept:
                grade_name = cancer_condition.grade_concept.concept_name.lower()
                if 'grade' in grade_name:
                    # Extract numeric grade
                    for i in range(1, 5):
                        if str(i) in grade_name or ['i', 'ii', 'iii', 'iv'][i-1] in grade_name:
                            data['biopsy_grade'] = i
                            break

            # Primary site
            if cancer_condition.primary_site_concept:
                data['staging_modalities'] = cancer_condition.primary_site_concept.concept_name

            # Metastatic status
            if cancer_condition.tnm_clinical_m == 'M1' or cancer_condition.tnm_pathologic_m == 'M1':
                data['metastatic_status'] = True
            elif cancer_condition.tnm_clinical_m == 'M0' or cancer_condition.tnm_pathologic_m == 'M0':
                data['metastatic_status'] = False

        return data

    def get_treatment_data(self, person):
        """Extract treatment information from TreatmentLine"""
        data = {}
        
        treatment_lines = TreatmentLine.objects.filter(person=person).order_by('line_number')
        
        if treatment_lines.exists():
            # Current treatment line
            current_line = treatment_lines.last()
            data['line_of_therapy'] = str(current_line.line_number)
            data['therapy_lines_count'] = treatment_lines.count()
            
            # Current regimen
            if current_line.regimen_name:
                data['concomitant_medications'] = current_line.regimen_name

            # Treatment history
            therapy_details = []
            for line in treatment_lines:
                line_info = {
                    'line': line.line_number,
                    'regimen': line.regimen_name,
                    'intent': line.treatment_intent,
                    'response': line.best_response,
                    'outcome': line.treatment_outcome
                }
                therapy_details.append(line_info)

            if len(therapy_details) >= 1:
                first_line = therapy_details[0]
                data['first_line_therapy'] = first_line['regimen']
                data['first_line_date'] = treatment_lines.first().line_start_date
                data['first_line_outcome'] = first_line['response']

            if len(therapy_details) >= 2:
                second_line = therapy_details[1]
                data['second_line_therapy'] = second_line['regimen']
                data['second_line_date'] = treatment_lines.filter(line_number=2).first().line_start_date
                data['second_line_outcome'] = second_line['response']

            if len(therapy_details) > 2:
                later_lines = therapy_details[2:]
                data['later_therapy'] = '; '.join([line['regimen'] for line in later_lines])
                data['later_date'] = treatment_lines.filter(line_number__gt=2).first().line_start_date
                data['later_outcome'] = later_lines[-1]['response']

            # Treatment types
            platinum_therapy = any(line.is_platinum_based for line in treatment_lines)
            immunotherapy = any(line.is_immunotherapy for line in treatment_lines)
            
            if platinum_therapy:
                data['prior_therapy'] = 'Platinum-based chemotherapy'
            if immunotherapy:
                data['prior_therapy'] = data.get('prior_therapy', '') + '; Immunotherapy'

        return data

    def get_vitals_data(self, person):
        """Extract vital signs data"""
        data = {}
        
        # Get most recent vital signs
        recent_vitals = VitalSignMeasurement.objects.filter(
            person=person
        ).order_by('-measurement_date')

        # Blood pressure
        bp_measurement = recent_vitals.filter(vital_sign_type='BLOOD_PRESSURE').first()
        if bp_measurement:
            data['systolic_blood_pressure'] = bp_measurement.systolic_bp
            data['diastolic_blood_pressure'] = bp_measurement.diastolic_bp

        # Weight
        weight_measurement = recent_vitals.filter(vital_sign_type='WEIGHT').first()
        if weight_measurement:
            weight_kg = weight_measurement.weight
            if weight_measurement.weight_unit == 'lb':
                weight_kg = weight_measurement.weight * Decimal('0.453592')
            data['weight'] = float(weight_kg)
            data['weight_units'] = 'kg'

        # Height
        height_measurement = recent_vitals.filter(vital_sign_type='HEIGHT').first()
        if height_measurement:
            height_cm = height_measurement.height
            if height_measurement.height_unit == 'in':
                height_cm = height_measurement.height * Decimal('2.54')
            data['height'] = float(height_cm)
            data['height_units'] = 'cm'

        # Heart rate
        hr_measurement = recent_vitals.filter(vital_sign_type='HEART_RATE').first()
        if hr_measurement:
            data['heartrate'] = hr_measurement.heart_rate

        return data

    def get_biomarker_data(self, person):
        """Extract biomarker information"""
        data = {}
        
        biomarkers = BiomarkerMeasurement.objects.filter(person=person).order_by('-measurement_date')
        
        # PD-L1
        pdl1_test = biomarkers.filter(biomarker_type='PD_L1').first()
        if pdl1_test:
            data['pd_l1_tumor_cels'] = int(pdl1_test.result_value) if pdl1_test.result_value else None
            data['pd_l1_assay'] = pdl1_test.antibody_clone

        # Hormone receptors
        er_test = biomarkers.filter(biomarker_type='ER').first()
        if er_test:
            data['estrogen_receptor_status'] = er_test.clinical_significance

        pr_test = biomarkers.filter(biomarker_type='PR').first()
        if pr_test:
            data['progesterone_receptor_status'] = pr_test.clinical_significance

        her2_test = biomarkers.filter(biomarker_type='HER2').first()
        if her2_test:
            data['her2_status'] = her2_test.clinical_significance

        # Triple negative status
        if er_test and pr_test and her2_test:
            is_tnbc = (er_test.clinical_significance == 'NEGATIVE' and 
                      pr_test.clinical_significance == 'NEGATIVE' and 
                      her2_test.clinical_significance == 'NEGATIVE')
            data['tnbc_status'] = is_tnbc

        return data

    def get_social_data(self, person):
        """Extract social determinants"""
        data = {}
        
        social_determinants = SocialDeterminant.objects.filter(person=person)
        
        for determinant in social_determinants:
            if determinant.determinant_category == 'EMPLOYMENT':
                data['no_pre_existing_conditions'] = determinant.value_as_string
            elif determinant.determinant_category == 'INSURANCE':
                data['concomitant_medication_details'] = determinant.value_as_string

        return data

    def get_behavior_data(self, person):
        """Extract health behaviors"""
        data = {}
        
        behaviors = HealthBehavior.objects.filter(person=person)
        
        for behavior in behaviors:
            if behavior.behavior_type == 'TOBACCO_USE':
                if behavior.current_status == 'NEVER':
                    data['no_tobacco_use_status'] = True
                    data['tobacco_use_details'] = 'Never smoker'
                elif behavior.current_status == 'FORMER':
                    data['no_tobacco_use_status'] = False
                    data['tobacco_use_details'] = f'Former smoker, quit {behavior.quit_date}'
                elif behavior.current_status == 'CURRENT':
                    data['no_tobacco_use_status'] = False
                    data['tobacco_use_details'] = 'Current smoker'

        return data

    def get_infection_data(self, person):
        """Extract infection status"""
        data = {}
        
        infections = InfectionStatus.objects.filter(person=person)
        
        for infection in infections:
            if infection.infection_type == 'HIV':
                data['no_hiv_status'] = infection.infection_status == 'NEGATIVE'
                data['hiv_status'] = infection.infection_status == 'POSITIVE'
            elif infection.infection_type == 'HEPATITIS_B':
                data['no_hepatitis_b_status'] = infection.infection_status == 'NEGATIVE'
                data['hepatitis_b_status'] = infection.infection_status == 'POSITIVE'
            elif infection.infection_type == 'HEPATITIS_C':
                data['no_hepatitis_c_status'] = infection.infection_status == 'NEGATIVE'
                data['hepatitis_c_status'] = infection.infection_status == 'POSITIVE'

        return data

    def get_assessment_data(self, person):
        """Extract tumor assessment data"""
        data = {}
        
        assessments = TumorAssessment.objects.filter(person=person).order_by('-assessment_date')
        
        if assessments.exists():
            latest_assessment = assessments.first()
            
            # Response mapping
            response_map = {
                'CR': 'Complete Response',
                'PR': 'Partial Response', 
                'SD': 'Stable Disease',
                'PD': 'Progressive Disease'
            }
            
            if latest_assessment.overall_response in response_map:
                data['best_response'] = response_map[latest_assessment.overall_response]

            # RECIST status
            if latest_assessment.target_lesion_sum:
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
            elif 'karnofsky' in concept_name and obs.value_as_number is not None:
                data['karnofsky_performance_score'] = int(obs.value_as_number)

        return data

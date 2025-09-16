from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date, datetime, timedelta
from omop_core.models import (
    Concept, Person, Location, ConditionOccurrence, VitalSignMeasurement,
    MeasurementExtension, ObservationExtension, PatientInfo,
    Vocabulary, Domain, ConceptClass
)
from omop_genomics.models import BiomarkerMeasurement, TumorAssessment
from omop_oncology.models import TreatmentLine, SocialDeterminant, HealthBehavior, InfectionStatus


class Command(BaseCommand):
    help = 'Create enhanced sample data to demonstrate PatientInfo population'

    def handle(self, *args, **options):
        # Create sample locations
        location_ny, _ = Location.objects.get_or_create(
            location_id=1001,
            defaults={
                'address_1': "123 Medical Center Dr",
                'city': "New York",
                'state': "NY",
                'zip': "10001",
                'county': "New York County",
                'country': "United States"
            }
        )
        
        # Create sample patient with enhanced data
        person, _ = Person.objects.get_or_create(
            person_id=4001,
            defaults={
                'gender_concept': self.get_or_create_concept(8532, "Female"),
                'year_of_birth': 1975,
                'month_of_birth': 3,
                'day_of_birth': 15,
                'birth_datetime': timezone.make_aware(datetime(1975, 3, 15, 10, 30)),
                'race_concept': self.get_or_create_concept(8527, "White"),
                'ethnicity_concept': self.get_or_create_concept(38003564, "Not Hispanic or Latino"),
                'location': location_ny,
                'primary_language_concept': self.get_or_create_concept(4180186, "English"),
                'language_skill_level': "NATIVE"
            }
        )
        
        # Create lung cancer condition with detailed staging
        lung_cancer, _ = ConditionOccurrence.objects.get_or_create(
            condition_occurrence_id=3001,
            defaults={
                'person': person,
                'condition_concept': self.get_or_create_concept(4115276, "Non-small cell lung cancer"),
                'condition_start_date': date(2023, 1, 15),
                'condition_start_datetime': timezone.make_aware(datetime(2023, 1, 15, 14, 0)),
                'condition_type_concept': self.get_or_create_concept(32020, "Initial"),
                'primary_site_concept': self.get_or_create_concept(4221847, "Upper lobe of right lung"),
                'histology_concept': self.get_or_create_concept(4195694, "Adenocarcinoma"),
                'behavior_concept': self.get_or_create_concept(4124400, "Malignant"),
                'grade_concept': self.get_or_create_concept(4191232, "Grade II"),
                'staging_system': "AJCC_8TH",
                'clinical_stage_group': "IIIA",
                'pathologic_stage_group': "IIIA",
                'tnm_clinical_t': "T2",
                'tnm_clinical_n': "N2",
                'tnm_clinical_m': "M0",
                'tnm_pathologic_t': "T2",
                'tnm_pathologic_n': "N2",
                'tnm_pathologic_m': "M0",
                'tumor_size_cm': Decimal('3.5'),
                'laterality': "RIGHT",
                'progression_status': "STABLE"
            }
        )
        
        # Create biomarker measurements
        BiomarkerMeasurement.objects.create(
            biomarker_measurement_id=2001,
            person=person,
            biomarker_concept=self.get_or_create_concept(4112853, "PD-L1"),
            measurement_date=date(2023, 1, 20),
            measurement_datetime=timezone.make_aware(datetime(2023, 1, 20, 9, 0)),
            biomarker_type="PD_L1",
            value_as_number=Decimal('65.0'),
            assay_method="IHC",
            clinical_significance="POSITIVE"
        )
        
        # Create treatment line
        TreatmentLine.objects.create(
            treatment_line_id=1001,
            person=person,
            line_number=1,
            line_start_date=date(2023, 2, 1),
            treatment_intent="CURATIVE",
            regimen_name="Carboplatin + Paclitaxel + Pembrolizumab",
            treatment_setting="OUTPATIENT",
            is_platinum_based=True,
            is_immunotherapy=True,
            is_chemotherapy=True,
            ecog_at_start=1,
            best_response="PR"
        )
        
        # Create tumor assessment
        TumorAssessment.objects.create(
            tumor_assessment_id=1001,
            person=person,
            assessment_date=date(2023, 4, 15),
            assessment_datetime=datetime(2023, 4, 15, 10, 0),
            assessment_method="CT_SCAN",
            overall_response="PR",
            progression_status="NO_PROGRESSION",
            target_lesion_sum=Decimal('4.2'),
            target_lesion_unit="cm",
            new_lesions=False,
            assessment_notes="Partial response with 30% reduction in target lesions"
        )
        
        # Create vital signs
        VitalSignMeasurement.objects.create(
            vital_sign_id=1001,
            person=person,
            measurement_date=date(2023, 2, 1),
            vital_sign_type="BLOOD_PRESSURE",
            systolic_bp=135,
            diastolic_bp=85,
            measurement_position="SITTING"
        )
        
        VitalSignMeasurement.objects.create(
            vital_sign_id=1002,
            person=person,
            measurement_date=date(2023, 2, 1),
            vital_sign_type="WEIGHT",
            weight=Decimal('68.5'),
            weight_unit="kg"
        )
        
        VitalSignMeasurement.objects.create(
            vital_sign_id=1003,
            person=person,
            measurement_date=date(2023, 2, 1),
            vital_sign_type="HEIGHT",
            height=Decimal('165'),
            height_unit="cm"
        )
        
        # Create social determinants
        SocialDeterminant.objects.create(
            social_determinant_id=1001,
            person=person,
            determinant_concept=self.get_or_create_concept(4183531, "Employment status"),
            assessment_date=date(2023, 1, 15),
            determinant_category="EMPLOYMENT",
            value_as_string="Employed full-time",
            risk_level="LOW"
        )
        
        SocialDeterminant.objects.create(
            social_determinant_id=1002,
            person=person,
            determinant_concept=self.get_or_create_concept(4058746, "Insurance coverage"),
            assessment_date=date(2023, 1, 15),
            determinant_category="INSURANCE",
            value_as_string="Private insurance",
            risk_level="LOW"
        )
        
        # Create health behaviors
        HealthBehavior.objects.create(
            health_behavior_id=1001,
            person=person,
            behavior_concept=self.get_or_create_concept(4209585, "Tobacco smoking"),
            assessment_date=date(2023, 1, 15),
            behavior_type="TOBACCO_USE",
            current_status="FORMER",
            duration_years=15,
            quit_date=date(2018, 6, 1),
            behavior_details="Quit 5 years ago, 1 pack per day for 15 years"
        )
        
        # Create infection status
        InfectionStatus.objects.create(
            infection_status_id=1001,
            person=person,
            infection_concept=self.get_or_create_concept(4265791, "HIV"),
            assessment_date=date(2023, 1, 15),
            infection_type="HIV",
            infection_status="NEGATIVE",
            test_method="ELISA"
        )
        
        # Create or update PatientInfo
        patient_info, created = PatientInfo.objects.get_or_create(
            patient_info_id=4001,
            defaults={
                'person': person,
                'last_updated': timezone.now(),
                # Demographics from Person
                'age': 48,
                'gender': 'Female',
                'race': 'White',
                'ethnicity': 'Not Hispanic or Latino',
                'primary_language': 'English',
                'language_skill_level': 'Native',
                # Location data
                'state': 'NY',
                'city': 'New York',
                'zip_code': '10001',
                'country': 'United States',
                # Disease information from ConditionOccurrence
                'primary_diagnosis': 'Non-small cell lung cancer',
                'cancer_stage': 'IIIA',
                'cancer_stage_system': 'AJCC 8th Edition',
                'tnm_t': 'T2',
                'tnm_n': 'N2',
                'tnm_m': 'M0',
                'histology': 'Adenocarcinoma',
                'tumor_grade': 'Grade II',
                'primary_site': 'Upper lobe of right lung',
                'tumor_size_cm': Decimal('3.5'),
                'metastatic_sites': '',
                # Treatment information from TreatmentLine
                'current_treatment_line': 1,
                'prior_therapies': '',
                'current_regimen': 'Carboplatin + Paclitaxel + Pembrolizumab',
                'treatment_intent': 'Curative',
                'prior_platinum_therapy': True,
                'prior_immunotherapy': False,
                'immunotherapy_type': 'PD-1 inhibitor',
                # Performance status
                'ecog_performance_status': 1,
                # Biomarkers from BiomarkerMeasurement
                'pdl1_expression': Decimal('65.0'),
                'pdl1_assay': '22C3',
                # Vital signs from VitalSignMeasurement
                'weight_kg': Decimal('68.5'),
                'height_cm': Decimal('165'),
                'bmi': Decimal('25.2'),  # Will be calculated
                'systolic_bp': 135,
                'diastolic_bp': 85,
                # Social determinants
                'employment_status': 'Employed full-time',
                'insurance_type': 'Private insurance',
                # Health behaviors
                'smoking_status': 'Former smoker',
                'smoking_pack_years': 15,
                # Infection status
                'hiv_status': 'Negative',
                # Response from TumorAssessment
                'best_response': 'Partial Response',
                'progression_free_survival_months': 3,  # Calculated from dates
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created enhanced sample data:\n'
                f'- Person: {person.person_id}\n'
                f'- Location: {location_ny.city}, {location_ny.state}\n'
                f'- Condition: {lung_cancer.condition_concept}\n'
                f'- Treatment Line: {TreatmentLine.objects.filter(person=person).count()}\n'
                f'- Biomarker Tests: {BiomarkerMeasurement.objects.filter(person=person).count()}\n'
                f'- Vital Signs: {VitalSignMeasurement.objects.filter(person=person).count()}\n'
                f'- Social Determinants: {SocialDeterminant.objects.filter(person=person).count()}\n'
                f'- Health Behaviors: {HealthBehavior.objects.filter(person=person).count()}\n'
                f'- Infection Status: {InfectionStatus.objects.filter(person=person).count()}\n'
                f'- Tumor Assessments: {TumorAssessment.objects.filter(person=person).count()}\n'
                f'- PatientInfo: {"Created" if created else "Updated"}'
            )
        )

    def get_or_create_concept(self, concept_id, concept_name):
        """Helper method to get or create a concept"""
        # First ensure we have the required vocabulary, domain, and concept class
        vocab, _ = Vocabulary.objects.get_or_create(
            vocabulary_id='SNOMED',
            defaults={
                'vocabulary_name': 'SNOMED CT',
                'vocabulary_reference': 'http://www.snomed.org/',
                'vocabulary_concept_id': 0
            }
        )
        
        domain, _ = Domain.objects.get_or_create(
            domain_id='General',
            defaults={
                'domain_name': 'General',
                'domain_concept_id': 0
            }
        )
        
        concept_class, _ = ConceptClass.objects.get_or_create(
            concept_class_id='General',
            defaults={
                'concept_class_name': 'General',
                'concept_class_concept_id': 0
            }
        )
        
        concept, created = Concept.objects.get_or_create(
            concept_id=concept_id,
            defaults={
                'concept_name': concept_name,
                'domain': domain,
                'vocabulary': vocab,
                'concept_class': concept_class,
                'standard_concept': 'S',
                'concept_code': str(concept_id),
                'valid_start_date': date(2000, 1, 1),
                'valid_end_date': date(2099, 12, 31),
                'invalid_reason': None
            }
        )
        return concept

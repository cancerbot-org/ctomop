"""
Generate 100 synthetic breast cancer patients for OMOP CDM tables

This script creates realistic synthetic data for breast cancer patients with:
- 50 TNBC (Triple-Negative Breast Cancer) patients
- 50 non-TNBC patients with varying ER/PR/HER2 status
- Complete demographic, clinical, and treatment data
- Genetic mutations appropriate for each subtype
- OMOP CDM v6.0 compliant data storage

Usage:
    python manage.py generate_breast_cancer_patients
"""

import random
import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from omop_core.models import (
    Person, Location, Concept, Vocabulary, Domain, ConceptClass,
    Measurement, Observation, ConditionOccurrence, DrugExposure, VisitOccurrence
)


class Command(BaseCommand):
    help = 'Generate 100 synthetic breast cancer patients (50 TNBC) for OMOP tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Total number of patients to generate (default: 100)',
        )
        parser.add_argument(
            '--tnbc-ratio',
            type=float,
            default=0.5,
            help='Ratio of TNBC patients (default: 0.5 = 50%)',
        )
        parser.add_argument(
            '--seed',
            type=int,
            default=42,
            help='Random seed for reproducible data generation',
        )

    def handle(self, *args, **options):
        count = options['count']
        tnbc_ratio = options['tnbc_ratio']
        seed = options['seed']
        
        random.seed(seed)
        
        self.stdout.write(f'Generating {count} synthetic breast cancer patients...')
        self.stdout.write(f'TNBC patients: {int(count * tnbc_ratio)} ({tnbc_ratio * 100}%)')
        
        # Create required concepts and vocabularies
        self.create_vocabularies_and_concepts()
        
        # Generate patients
        tnbc_count = int(count * tnbc_ratio)
        non_tnbc_count = count - tnbc_count
        
        with transaction.atomic():
            # Generate TNBC patients
            for i in range(tnbc_count):
                self.generate_patient(is_tnbc=True, patient_num=i+1)
                
            # Generate non-TNBC patients
            for i in range(non_tnbc_count):
                self.generate_patient(is_tnbc=False, patient_num=tnbc_count+i+1)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated {count} synthetic breast cancer patients:\n'
                f'  TNBC patients: {tnbc_count}\n'
                f'  Non-TNBC patients: {non_tnbc_count}\n'
                f'  Total: {count}'
            )
        )

    def create_vocabularies_and_concepts(self):
        """Create required OMOP vocabularies and concepts"""
        
        # Create vocabularies
        vocabularies = [
            ('SNOMED', 'Systematic Nomenclature of Medicine Clinical Terms', 'SNOMED CT', '2023-07'),
            ('LOINC', 'Logical Observation Identifiers Names and Codes', 'LOINC', '2.76'),
            ('Gender', 'OMOP Gender', 'OMOP generated', '1.0'),
            ('Race', 'OMOP Race', 'OMOP generated', '1.0'),
            ('Ethnicity', 'OMOP Ethnicity', 'OMOP generated', '1.0'),
        ]
        
        for vocab_id, name, reference, version in vocabularies:
            Vocabulary.objects.get_or_create(
                vocabulary_id=vocab_id,
                defaults={
                    'vocabulary_name': name,
                    'vocabulary_reference': reference,
                    'vocabulary_version': version,
                    'vocabulary_concept_id': 0
                }
            )

        # Create domains
        domains = [
            ('Gender', 'Gender'),
            ('Race', 'Race'),
            ('Ethnicity', 'Ethnicity'),
            ('Condition', 'Condition'),
            ('Measurement', 'Measurement'),
            ('Observation', 'Observation'),
            ('Drug', 'Drug'),
        ]
        
        for domain_id, name in domains:
            Domain.objects.get_or_create(
                domain_id=domain_id,
                defaults={
                    'domain_name': name,
                    'domain_concept_id': 0
                }
            )

        # Create concept classes
        concept_classes = [
            ('Clinical Finding', 'Clinical Finding'),
            ('Procedure', 'Procedure'),
            ('Lab Test', 'Lab Test'),
            ('Gender', 'Gender'),
            ('Race', 'Race'),
            ('Ethnicity', 'Ethnicity'),
        ]
        
        for class_id, name in concept_classes:
            ConceptClass.objects.get_or_create(
                concept_class_id=class_id,
                defaults={
                    'concept_class_name': name,
                    'concept_class_concept_id': 0
                }
            )

        # Create essential concepts
        self.create_essential_concepts()

    def create_essential_concepts(self):
        """Create essential concepts for breast cancer patients"""
        
        # Get vocabularies and domains
        snomed_vocab = Vocabulary.objects.get(vocabulary_id='SNOMED')
        loinc_vocab = Vocabulary.objects.get(vocabulary_id='LOINC')
        gender_vocab = Vocabulary.objects.get(vocabulary_id='Gender')
        race_vocab = Vocabulary.objects.get(vocabulary_id='Race')
        ethnicity_vocab = Vocabulary.objects.get(vocabulary_id='Ethnicity')
        
        condition_domain = Domain.objects.get(domain_id='Condition')
        measurement_domain = Domain.objects.get(domain_id='Measurement')
        observation_domain = Domain.objects.get(domain_id='Observation')
        gender_domain = Domain.objects.get(domain_id='Gender')
        race_domain = Domain.objects.get(domain_id='Race')
        ethnicity_domain = Domain.objects.get(domain_id='Ethnicity')
        
        clinical_finding_class = ConceptClass.objects.get(concept_class_id='Clinical Finding')
        lab_test_class = ConceptClass.objects.get(concept_class_id='Lab Test')
        gender_class = ConceptClass.objects.get(concept_class_id='Gender')
        race_class = ConceptClass.objects.get(concept_class_id='Race')
        ethnicity_class = ConceptClass.objects.get(concept_class_id='Ethnicity')

        # Essential concepts for patient generation
        concepts = [
            # Gender concepts
            (8507, 'MALE', 'M', gender_domain, gender_vocab, gender_class, 'S'),
            (8532, 'FEMALE', 'F', gender_domain, gender_vocab, gender_class, 'S'),
            
            # Race concepts
            (8527, 'White', 'White', race_domain, race_vocab, race_class, 'S'),
            (8516, 'Black or African American', 'Black', race_domain, race_vocab, race_class, 'S'),
            (8515, 'Asian', 'Asian', race_domain, race_vocab, race_class, 'S'),
            
            # Ethnicity concepts
            (38003563, 'Hispanic or Latino', 'Hispanic', ethnicity_domain, ethnicity_vocab, ethnicity_class, 'S'),
            (38003564, 'Not Hispanic or Latino', 'Not Hispanic', ethnicity_domain, ethnicity_vocab, ethnicity_class, 'S'),
            
            # Breast cancer diagnosis
            (4112853, 'Malignant tumor of breast', '174.9', condition_domain, snomed_vocab, clinical_finding_class, 'S'),
            (4163261, 'Triple negative breast cancer', '8500/3', condition_domain, snomed_vocab, clinical_finding_class, 'S'),
            
            # Biomarker measurements - LOINC codes
            (3025023, 'Estrogen receptor Ag', '16112-5', measurement_domain, loinc_vocab, lab_test_class, 'S'),
            (3020891, 'Progesterone receptor Ag', '16113-3', measurement_domain, loinc_vocab, lab_test_class, 'S'),
            (3003740, 'HER2 receptor', '48676-1', measurement_domain, loinc_vocab, lab_test_class, 'S'),
            
            # Genetic test LOINC codes
            (3023103, 'BRCA1 gene mutations', '21636-6', measurement_domain, loinc_vocab, lab_test_class, 'S'),
            (3005771, 'BRCA2 gene mutations', '21637-4', measurement_domain, loinc_vocab, lab_test_class, 'S'),
            (3019550, 'TP53 gene mutations', '21667-1', measurement_domain, loinc_vocab, lab_test_class, 'S'),
            
            # Measurement result concepts
            (4181412, 'Positive', 'POS', measurement_domain, snomed_vocab, clinical_finding_class, 'S'),
            (4132135, 'Negative', 'NEG', measurement_domain, snomed_vocab, clinical_finding_class, 'S'),
            (45884084, 'Equivocal', 'E', measurement_domain, snomed_vocab, clinical_finding_class, 'S'),
            
            # Mutation origin and interpretation
            (255395001, 'Germline mutation', 'germline', observation_domain, snomed_vocab, clinical_finding_class, 'S'),
            (255461003, 'Somatic mutation', 'somatic', observation_domain, snomed_vocab, clinical_finding_class, 'S'),
            (30166007, 'Pathogenic', 'pathogenic', observation_domain, snomed_vocab, clinical_finding_class, 'S'),
            (10828004, 'Benign', 'benign', observation_domain, snomed_vocab, clinical_finding_class, 'S'),
            (42425007, 'Variant of unknown significance', 'vus', observation_domain, snomed_vocab, clinical_finding_class, 'S'),
            
            # Vital signs and lab values
            (3004249, 'Systolic blood pressure', '8480-6', measurement_domain, loinc_vocab, lab_test_class, 'S'),
            (3012888, 'Diastolic blood pressure', '8462-4', measurement_domain, loinc_vocab, lab_test_class, 'S'),
            (3025315, 'Body weight', '29463-7', measurement_domain, loinc_vocab, lab_test_class, 'S'),
            (3036277, 'Body height', '8302-2', measurement_domain, loinc_vocab, lab_test_class, 'S'),
            (3013682, 'Hemoglobin', '718-7', measurement_domain, loinc_vocab, lab_test_class, 'S'),
            (3016723, 'Creatinine', '2160-0', measurement_domain, loinc_vocab, lab_test_class, 'S'),
        ]

        for concept_id, name, code, domain, vocab, concept_class, standard in concepts:
            Concept.objects.get_or_create(
                concept_id=concept_id,
                defaults={
                    'concept_name': name,
                    'domain': domain,
                    'vocabulary': vocab,
                    'concept_class': concept_class,
                    'standard_concept': standard,
                    'concept_code': code,
                    'valid_start_date': date(2000, 1, 1),
                    'valid_end_date': date(2099, 12, 31),
                }
            )

    def generate_patient(self, is_tnbc, patient_num):
        """Generate a single synthetic breast cancer patient"""
        
        # Generate demographics
        # Start from a higher ID to avoid conflicts
        person_id = 20000 + patient_num
        age = random.randint(35, 75)
        birth_year = date.today().year - age
        
        # Create location
        location = self.create_location(patient_num)
        
        # Create person
        person = self.create_person(person_id, birth_year, location)
        
        # Create visit
        visit = self.create_visit(person)
        
        # Create breast cancer diagnosis
        self.create_breast_cancer_diagnosis(person, visit, is_tnbc)
        
        # Create biomarker measurements
        self.create_biomarker_measurements(person, visit, is_tnbc)
        
        # Create genetic mutations
        self.create_genetic_mutations(person, visit, is_tnbc)
        
        # Create vital signs and lab values
        self.create_vital_signs_and_labs(person, visit)
        
        # Create treatment history
        self.create_treatment_history(person, visit, is_tnbc)
        
        self.stdout.write(f'Generated patient {person_id} ({"TNBC" if is_tnbc else "non-TNBC"})')

    def create_location(self, patient_num):
        """Create a location for the patient"""
        
        locations = [
            ('New York', 'NY', '10001', 'US', 40.7128, -74.0060),
            ('Los Angeles', 'CA', '90001', 'US', 34.0522, -118.2437),
            ('Chicago', 'IL', '60601', 'US', 41.8781, -87.6298),
            ('Houston', 'TX', '77001', 'US', 29.7604, -95.3698),
            ('Boston', 'MA', '02101', 'US', 42.3601, -71.0589),
        ]
        
        city, state, zip_code, country, lat, lon = random.choice(locations)
        
        # Use filter then create to handle existing locations properly
        existing_location = Location.objects.filter(
            city=city,
            state=state,
            zip=zip_code,
            country=country
        ).first()
        
        if existing_location:
            location = existing_location
        else:
            # Find next available location_id
            max_location_id = Location.objects.aggregate(max_id=Max('location_id'))['max_id'] or 20000
            location = Location.objects.create(
                location_id=max_location_id + 1,
                city=city,
                state=state,
                zip=zip_code,
                country=country,
                latitude=Decimal(str(lat)),
                longitude=Decimal(str(lon))
            )
        
        return location

    def create_person(self, person_id, birth_year, location):
        """Create a person record"""
        
        # Get concepts
        female_concept = Concept.objects.get(concept_id=8532)  # Female
        
        # Random race/ethnicity
        race_concepts = [8527, 8516, 8515]  # White, Black, Asian
        ethnicity_concepts = [38003563, 38003564]  # Hispanic, Not Hispanic
        
        race_concept = Concept.objects.get(concept_id=random.choice(race_concepts))
        ethnicity_concept = Concept.objects.get(concept_id=random.choice(ethnicity_concepts))
        
        person = Person.objects.create(
            person_id=person_id,
            gender_concept=female_concept,
            year_of_birth=birth_year,
            month_of_birth=random.randint(1, 12),
            day_of_birth=random.randint(1, 28),
            race_concept=race_concept,
            ethnicity_concept=ethnicity_concept,
            location=location
        )
        
        return person

    def create_visit(self, person):
        """Create a visit occurrence"""
        
        visit_date = date.today() - timedelta(days=random.randint(30, 365))
        
        # Create a basic visit concept (outpatient visit)
        visit_concept, _ = Concept.objects.get_or_create(
            concept_id=9202,
            defaults={
                'concept_name': 'Outpatient Visit',
                'domain': Domain.objects.get(domain_id='Observation'),
                'vocabulary': Vocabulary.objects.get(vocabulary_id='SNOMED'),
                'concept_class': ConceptClass.objects.get(concept_class_id='Clinical Finding'),
                'standard_concept': 'S',
                'concept_code': '185349003',
                'valid_start_date': date(2000, 1, 1),
                'valid_end_date': date(2099, 12, 31),
            }
        )
        
        visit_type_concept, _ = Concept.objects.get_or_create(
            concept_id=44818517,
            defaults={
                'concept_name': 'EHR record',
                'domain': Domain.objects.get(domain_id='Observation'),
                'vocabulary': Vocabulary.objects.get(vocabulary_id='SNOMED'),
                'concept_class': ConceptClass.objects.get(concept_class_id='Clinical Finding'),
                'standard_concept': 'S',
                'concept_code': 'EHR',
                'valid_start_date': date(2000, 1, 1),
                'valid_end_date': date(2099, 12, 31),
            }
        )
        
        visit = VisitOccurrence.objects.create(
            visit_occurrence_id=30000 + person.person_id,
            person=person,
            visit_concept=visit_concept,
            visit_start_date=visit_date,
            visit_end_date=visit_date,
            visit_type_concept=visit_type_concept
        )
        
        return visit

    def create_breast_cancer_diagnosis(self, person, visit, is_tnbc):
        """Create breast cancer diagnosis"""
        
        if is_tnbc:
            condition_concept = Concept.objects.get(concept_id=4163261)  # TNBC
        else:
            condition_concept = Concept.objects.get(concept_id=4112853)  # General breast cancer
        
        # Create condition type concept
        condition_type_concept, _ = Concept.objects.get_or_create(
            concept_id=32020,
            defaults={
                'concept_name': 'EHR Chief Complaint',
                'domain': Domain.objects.get(domain_id='Observation'),
                'vocabulary': Vocabulary.objects.get(vocabulary_id='SNOMED'),
                'concept_class': ConceptClass.objects.get(concept_class_id='Clinical Finding'),
                'standard_concept': 'S',
                'concept_code': 'EHR-CC',
                'valid_start_date': date(2000, 1, 1),
                'valid_end_date': date(2099, 12, 31),
            }
        )
        
        diagnosis_date = visit.visit_start_date - timedelta(days=random.randint(30, 365))
        
        ConditionOccurrence.objects.create(
            condition_occurrence_id=40000 + person.person_id,
            person=person,
            condition_concept=condition_concept,
            condition_start_date=diagnosis_date,
            condition_type_concept=condition_type_concept,
            visit_occurrence=visit
        )

    def create_biomarker_measurements(self, person, visit, is_tnbc):
        """Create biomarker measurements (ER, PR, HER2)"""
        
        measurement_type_concept, _ = Concept.objects.get_or_create(
            concept_id=44818702,
            defaults={
                'concept_name': 'Lab result',
                'domain': Domain.objects.get(domain_id='Measurement'),
                'vocabulary': Vocabulary.objects.get(vocabulary_id='SNOMED'),
                'concept_class': ConceptClass.objects.get(concept_class_id='Lab Test'),
                'standard_concept': 'S',
                'concept_code': 'LAB',
                'valid_start_date': date(2000, 1, 1),
                'valid_end_date': date(2099, 12, 31),
            }
        )
        
        measurement_date = visit.visit_start_date
        measurement_id_base = 50000 + (person.person_id * 10)
        
        # Get result concepts
        positive_concept = Concept.objects.get(concept_id=4181412)
        negative_concept = Concept.objects.get(concept_id=4132135)
        equivocal_concept = Concept.objects.get(concept_id=45884084)
        
        if is_tnbc:
            # TNBC: ER-, PR-, HER2-
            biomarkers = [
                (3025023, negative_concept, 'ER'),  # ER negative
                (3020891, negative_concept, 'PR'),  # PR negative
                (3003740, negative_concept, 'HER2'),  # HER2 negative
            ]
        else:
            # Non-TNBC: Random combinations but not all negative
            er_status = random.choice([positive_concept, negative_concept])
            pr_status = random.choice([positive_concept, negative_concept])
            her2_status = random.choice([positive_concept, negative_concept, equivocal_concept])
            
            # Ensure at least one is positive (not TNBC)
            if er_status == negative_concept and pr_status == negative_concept and her2_status == negative_concept:
                er_status = positive_concept  # Make ER positive
            
            biomarkers = [
                (3025023, er_status, 'ER'),
                (3020891, pr_status, 'PR'),
                (3003740, her2_status, 'HER2'),
            ]
        
        for i, (concept_id, result_concept, marker) in enumerate(biomarkers):
            measurement_concept = Concept.objects.get(concept_id=concept_id)
            
            Measurement.objects.create(
                measurement_id=measurement_id_base + i + 1,
                person=person,
                measurement_concept=measurement_concept,
                measurement_date=measurement_date,
                measurement_type_concept=measurement_type_concept,
                value_as_concept=result_concept,
                visit_occurrence=visit
            )

    def create_genetic_mutations(self, person, visit, is_tnbc):
        """Create genetic mutation measurements"""
        
        measurement_type_concept = Concept.objects.get(concept_id=44818702)  # Lab result
        measurement_date = visit.visit_start_date
        measurement_id_base = 60000 + (person.person_id * 10)
        
        # Get mutation concepts
        germline_concept = Concept.objects.get(concept_id=255395001)
        somatic_concept = Concept.objects.get(concept_id=255461003)
        pathogenic_concept = Concept.objects.get(concept_id=30166007)
        benign_concept = Concept.objects.get(concept_id=10828004)
        vus_concept = Concept.objects.get(concept_id=42425007)
        
        mutations = []
        
        if is_tnbc:
            # TNBC patients more likely to have BRCA mutations
            if random.random() < 0.3:  # 30% chance of BRCA1 mutation
                mutations.append({
                    'gene_concept_id': 3023103,  # BRCA1
                    'gene': 'brca1',
                    'variant': f'c.{random.randint(100, 5000)}G>A',
                    'origin': germline_concept,
                    'interpretation': pathogenic_concept,
                })
            
            if random.random() < 0.2:  # 20% chance of BRCA2 mutation
                mutations.append({
                    'gene_concept_id': 3005771,  # BRCA2
                    'gene': 'brca2',
                    'variant': f'c.{random.randint(100, 5000)}C>T',
                    'origin': germline_concept,
                    'interpretation': pathogenic_concept,
                })
            
            if random.random() < 0.5:  # 50% chance of TP53 mutation
                mutations.append({
                    'gene_concept_id': 3019550,  # TP53
                    'gene': 'tp53',
                    'variant': f'c.{random.randint(100, 1000)}G>T',
                    'origin': somatic_concept,
                    'interpretation': random.choice([pathogenic_concept, vus_concept]),
                })
        else:
            # Non-TNBC patients
            if random.random() < 0.1:  # 10% chance of BRCA1 mutation
                mutations.append({
                    'gene_concept_id': 3023103,  # BRCA1
                    'gene': 'brca1',
                    'variant': f'c.{random.randint(100, 5000)}G>A',
                    'origin': germline_concept,
                    'interpretation': random.choice([pathogenic_concept, benign_concept, vus_concept]),
                })
            
            if random.random() < 0.2:  # 20% chance of TP53 mutation
                mutations.append({
                    'gene_concept_id': 3019550,  # TP53
                    'gene': 'tp53',
                    'variant': f'c.{random.randint(100, 1000)}A>G',
                    'origin': somatic_concept,
                    'interpretation': random.choice([pathogenic_concept, benign_concept, vus_concept]),
                })
        
        # Create measurements for each mutation
        for i, mutation in enumerate(mutations):
            gene_concept = Concept.objects.get(concept_id=mutation['gene_concept_id'])
            
            Measurement.objects.create(
                measurement_id=measurement_id_base + i + 1,
                person=person,
                measurement_concept=gene_concept,
                measurement_date=measurement_date,
                measurement_type_concept=measurement_type_concept,
                value_as_string=mutation['variant'],
                qualifier_concept=mutation['origin'],
                value_as_concept=mutation['interpretation'],
                visit_occurrence=visit
            )

    def create_vital_signs_and_labs(self, person, visit):
        """Create vital signs and laboratory measurements"""
        
        measurement_type_concept = Concept.objects.get(concept_id=44818702)  # Lab result
        measurement_date = visit.visit_start_date
        measurement_id_base = 70000 + (person.person_id * 10)
        
        # Vital signs and lab values
        measurements = [
            (3004249, random.randint(110, 140), None, 'Systolic BP'),  # Systolic BP
            (3012888, random.randint(70, 90), None, 'Diastolic BP'),   # Diastolic BP
            (3025315, random.uniform(50, 90), None, 'Weight'),         # Weight (kg)
            (3036277, random.randint(150, 180), None, 'Height'),       # Height (cm)
            (3013682, random.uniform(10.5, 15.5), None, 'Hemoglobin'), # Hemoglobin
            (3016723, random.uniform(0.6, 1.2), None, 'Creatinine'),   # Creatinine
        ]
        
        for i, (concept_id, value, unit_concept_id, name) in enumerate(measurements):
            measurement_concept = Concept.objects.get(concept_id=concept_id)
            
            Measurement.objects.create(
                measurement_id=measurement_id_base + i + 1,
                person=person,
                measurement_concept=measurement_concept,
                measurement_date=measurement_date,
                measurement_type_concept=measurement_type_concept,
                value_as_number=Decimal(str(value)),
                visit_occurrence=visit
            )

    def create_treatment_history(self, person, visit, is_tnbc):
        """Create treatment history (simplified)"""
        
        # Create drug type concept
        drug_type_concept, _ = Concept.objects.get_or_create(
            concept_id=38000177,
            defaults={
                'concept_name': 'Prescription written',
                'domain': Domain.objects.get(domain_id='Drug'),
                'vocabulary': Vocabulary.objects.get(vocabulary_id='SNOMED'),
                'concept_class': ConceptClass.objects.get(concept_class_id='Clinical Finding'),
                'standard_concept': 'S',
                'concept_code': 'RX',
                'valid_start_date': date(2000, 1, 1),
                'valid_end_date': date(2099, 12, 31),
            }
        )
        
        # Create drug concepts for common breast cancer treatments
        if is_tnbc:
            treatments = [
                (1308216, 'Carboplatin'),  # Platinum-based chemotherapy
                (1357900, 'Paclitaxel'),   # Taxane
                (1551099, 'Pembrolizumab'), # Immunotherapy
            ]
        else:
            treatments = [
                (1551099, 'Tamoxifen'),    # Hormone therapy
                (1308216, 'Doxorubicin'),  # Chemotherapy
                (1357900, 'Paclitaxel'),   # Taxane
            ]
        
        treatment_start = visit.visit_start_date + timedelta(days=random.randint(7, 30))
        
        for i, (concept_id, drug_name) in enumerate(treatments):
            # Create drug concept if it doesn't exist
            drug_concept, _ = Concept.objects.get_or_create(
                concept_id=concept_id,
                defaults={
                    'concept_name': drug_name,
                    'domain': Domain.objects.get(domain_id='Drug'),
                    'vocabulary': Vocabulary.objects.get(vocabulary_id='SNOMED'),
                    'concept_class': ConceptClass.objects.get(concept_class_id='Clinical Finding'),
                    'standard_concept': 'S',
                    'concept_code': str(concept_id),
                    'valid_start_date': date(2000, 1, 1),
                    'valid_end_date': date(2099, 12, 31),
                }
            )
            
            DrugExposure.objects.create(
                drug_exposure_id=80000 + (person.person_id * 10) + i,
                person=person,
                drug_concept=drug_concept,
                drug_exposure_start_date=treatment_start,
                drug_exposure_end_date=treatment_start + timedelta(days=random.randint(21, 84)),
                drug_type_concept=drug_type_concept,
                visit_occurrence=visit
            )

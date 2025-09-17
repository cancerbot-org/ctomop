from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import date
from omop_core.models import Concept, Measurement, Person


class Command(BaseCommand):
    help = 'Migrate vital signs data from custom tables to standard OMOP Measurement table'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed migration information',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run')
        verbose = options.get('verbose')

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )

        # Create or ensure vital sign concepts exist
        vital_sign_concepts = self.create_vital_sign_concepts(dry_run, verbose)
        
        # Get measurement type concept
        measurement_type_concept = self.get_measurement_type_concept(dry_run, verbose)
        
        # Migration would go here if VitalSignMeasurement data existed
        self.stdout.write(
            self.style.SUCCESS(
                'Migration template ready. To use:\n'
                '1. Query existing VitalSignMeasurement records\n'
                '2. Convert each record to appropriate Measurement records\n'
                '3. Use LOINC concepts for standardized measurement types\n'
                '4. Split blood pressure into separate systolic/diastolic records'
            )
        )

    def create_vital_sign_concepts(self, dry_run, verbose):
        """Create or ensure vital sign LOINC concepts exist"""
        concepts = {}
        
        vital_signs = [
            (3004249, '8480-6', 'Systolic blood pressure'),
            (3012888, '8462-4', 'Diastolic blood pressure'),
            (3027018, '8867-4', 'Heart rate'),
            (3025315, '29463-7', 'Body weight'),
            (3036277, '8302-2', 'Body height'),
            (3038553, '39156-5', 'Body mass index'),
            (3020891, '8310-5', 'Body temperature'),
            (3016502, '2708-6', 'Oxygen saturation'),
        ]
        
        for concept_id, loinc_code, concept_name in vital_signs:
            if not dry_run:
                concept, created = Concept.objects.get_or_create(
                    concept_id=concept_id,
                    defaults={
                        'concept_name': concept_name,
                        'domain_id': 'Measurement',
                        'vocabulary_id': 'LOINC',
                        'concept_class_id': 'Clinical Observation',
                        'concept_code': loinc_code,
                        'standard_concept': 'S',
                        'valid_start_date': date(1970, 1, 1),
                        'valid_end_date': date(2099, 12, 31)
                    }
                )
                concepts[loinc_code] = concept
                
                if verbose:
                    status = "Created" if created else "Found existing"
                    self.stdout.write(f"{status} concept: {concept_name} ({loinc_code})")
            else:
                if verbose:
                    self.stdout.write(f"Would ensure concept: {concept_name} ({loinc_code})")
        
        return concepts

    def get_measurement_type_concept(self, dry_run, verbose):
        """Get or create measurement type concept"""
        if not dry_run:
            concept, created = Concept.objects.get_or_create(
                concept_id=44818701,  # EHR concept
                defaults={
                    'concept_name': 'EHR',
                    'domain_id': 'Type Concept',
                    'vocabulary_id': 'Type Concept',
                    'concept_class_id': 'Type Concept',
                    'concept_code': 'EHR',
                    'valid_start_date': date(1970, 1, 1),
                    'valid_end_date': date(2099, 12, 31)
                }
            )
            
            if verbose:
                status = "Created" if created else "Found existing"
                self.stdout.write(f"{status} measurement type concept: EHR")
                
            return concept
        else:
            if verbose:
                self.stdout.write("Would ensure measurement type concept: EHR")
            return None

    def create_sample_measurements(self, person_id, dry_run, verbose):
        """Example of how to create OMOP-compliant vital sign measurements"""
        if dry_run:
            self.stdout.write(f"Would create sample measurements for person {person_id}")
            return
            
        try:
            person = Person.objects.get(person_id=person_id)
            concepts = self.create_vital_sign_concepts(dry_run=False, verbose=False)
            measurement_type = self.get_measurement_type_concept(dry_run=False, verbose=False)
            
            # Example: Create systolic blood pressure measurement
            systolic_measurement = Measurement.objects.create(
                measurement_id=None,  # Auto-generated
                person=person,
                measurement_concept=concepts['8480-6'],  # Systolic BP
                measurement_date=date.today(),
                measurement_type_concept=measurement_type,
                value_as_number=Decimal('120')
            )
            
            # Example: Create diastolic blood pressure measurement
            diastolic_measurement = Measurement.objects.create(
                measurement_id=None,  # Auto-generated
                person=person,
                measurement_concept=concepts['8462-4'],  # Diastolic BP
                measurement_date=date.today(),
                measurement_type_concept=measurement_type,
                value_as_number=Decimal('80')
            )
            
            if verbose:
                self.stdout.write(
                    f"Created sample measurements for person {person_id}:\n"
                    f"- Systolic BP: {systolic_measurement.measurement_id}\n"
                    f"- Diastolic BP: {diastolic_measurement.measurement_id}"
                )
                
        except Person.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Person with ID {person_id} not found')
            )

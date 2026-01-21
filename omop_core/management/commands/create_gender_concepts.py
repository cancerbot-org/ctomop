from django.core.management.base import BaseCommand
from omop_core.models import Concept, Vocabulary, Domain, ConceptClass


class Command(BaseCommand):
    help = 'Create standard OMOP gender concepts'

    def handle(self, *args, **options):
        # Create or get the Gender domain
        domain, _ = Domain.objects.get_or_create(
            domain_id='Gender',
            defaults={'domain_name': 'Gender', 'domain_concept_id': 0}
        )
        
        # Create or get Gender vocabulary
        vocabulary, _ = Vocabulary.objects.get_or_create(
            vocabulary_id='Gender',
            defaults={
                'vocabulary_name': 'OMOP Gender',
                'vocabulary_reference': 'OMOP generated',
                'vocabulary_version': '1.0',
                'vocabulary_concept_id': 0
            }
        )
        
        # Create or get concept class
        concept_class, _ = ConceptClass.objects.get_or_create(
            concept_class_id='Gender',
            defaults={
                'concept_class_name': 'Gender',
                'concept_class_concept_id': 0
            }
        )
        
        # Standard OMOP gender concepts
        gender_concepts = [
            {
                'concept_id': 8507,
                'concept_name': 'MALE',
                'domain_id': 'Gender',
                'vocabulary_id': 'Gender',
                'concept_class_id': 'Gender',
                'standard_concept': 'S',
                'concept_code': 'M',
                'valid_start_date': '1970-01-01',
                'valid_end_date': '2099-12-31',
                'invalid_reason': None
            },
            {
                'concept_id': 8532,
                'concept_name': 'FEMALE',
                'domain_id': 'Gender',
                'vocabulary_id': 'Gender',
                'concept_class_id': 'Gender',
                'standard_concept': 'S',
                'concept_code': 'F',
                'valid_start_date': '1970-01-01',
                'valid_end_date': '2099-12-31',
                'invalid_reason': None
            },
            {
                'concept_id': 8551,
                'concept_name': 'UNKNOWN',
                'domain_id': 'Gender',
                'vocabulary_id': 'Gender',
                'concept_class_id': 'Gender',
                'standard_concept': 'S',
                'concept_code': 'U',
                'valid_start_date': '1970-01-01',
                'valid_end_date': '2099-12-31',
                'invalid_reason': None
            },
            {
                'concept_id': 8570,
                'concept_name': 'AMBIGUOUS',
                'domain_id': 'Gender',
                'vocabulary_id': 'Gender',
                'concept_class_id': 'Gender',
                'standard_concept': 'S',
                'concept_code': 'A',
                'valid_start_date': '1970-01-01',
                'valid_end_date': '2099-12-31',
                'invalid_reason': None
            }
        ]
        
        created_count = 0
        for concept_data in gender_concepts:
            concept, created = Concept.objects.get_or_create(
                concept_id=concept_data['concept_id'],
                defaults=concept_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created concept: {concept.concept_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Concept already exists: {concept.concept_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} gender concepts')
        )

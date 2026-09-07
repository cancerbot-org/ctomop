"""Auto-approve ICD10 (HT-One) mappings that overlap with approved ICD10CM
(Athena) mappings.

For each ICD10 ``proposed`` row whose ``source_code`` matches an ICD10CM
``approved`` row, copy the ``target_concept`` and mark it approved.  This is a
one-time catch-up: after the ICD-10-CM and ICD-10 tabs are merged, new codes
go through the normal curation flow.

Safe to re-run: already-approved ICD10 rows are skipped.

Usage::

    # Preview what would change
    python manage.py apply_icd10cm_mappings --dry-run

    # Apply
    python manage.py apply_icd10cm_mappings
"""
import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from omop_core.models import SourceCodeConceptMapping

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Auto-approve ICD10 mappings that overlap with approved ICD10CM mappings.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Report what would change without writing.',
        )

    def handle(self, **options):
        dry_run = options['dry_run']

        # Build lookup: source_code → approved ICD10CM row
        approved_icd10cm = {
            row.source_code: row
            for row in SourceCodeConceptMapping.objects.filter(
                source_vocabulary_id='ICD10CM',
                status='approved',
                target_concept__isnull=False,
            ).select_related('target_concept')
        }
        self.stdout.write(f'Approved ICD10CM mappings: {len(approved_icd10cm)}')

        # Find proposed ICD10 rows whose source_code overlaps
        pending_icd10 = SourceCodeConceptMapping.objects.filter(
            source_vocabulary_id='ICD10',
            status='proposed',
            source_code__in=approved_icd10cm.keys(),
        )
        count = pending_icd10.count()
        self.stdout.write(f'ICD10 proposed rows with ICD10CM overlap: {count}')

        if count == 0:
            self.stdout.write('Nothing to do.')
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'[DRY RUN] Would approve {count} ICD10 rows. '
                'Re-run without --dry-run to apply.'
            ))
            return

        updated = 0
        with transaction.atomic():
            for row in pending_icd10.iterator():
                donor = approved_icd10cm[row.source_code]
                row.target_concept = donor.target_concept
                row.status = 'approved'
                row.origin_system = (
                    f'{row.origin_system}; auto-approved from ICD10CM'
                    if row.origin_system
                    else 'auto-approved from ICD10CM'
                )
                row.save(update_fields=[
                    'target_concept', 'status', 'origin_system',
                ])
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Approved {updated} ICD10 rows from ICD10CM mappings.'
        ))

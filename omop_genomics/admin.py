from django.contrib import admin
from .models import (
    Specimen, GenomicVariantOccurrence, MolecularSequence, 
    GenomicVariantAnnotation, GenomicTestResult
)


@admin.register(Specimen)
class SpecimenAdmin(admin.ModelAdmin):
    list_display = ('specimen_id', 'person', 'specimen_concept', 'specimen_date')
    list_filter = ('specimen_concept', 'specimen_type_concept')
    search_fields = ('specimen_id', 'person__person_id')
    date_hierarchy = 'specimen_date'


@admin.register(GenomicVariantOccurrence)
class GenomicVariantOccurrenceAdmin(admin.ModelAdmin):
    list_display = ('genomic_variant_occurrence_id', 'person', 'genomic_variant_concept', 'gene_concept')
    list_filter = ('genomic_variant_concept', 'genomic_variant_type_concept', 'gene_concept')
    search_fields = ('genomic_variant_occurrence_id', 'person__person_id', 'genomic_variant_name')


@admin.register(MolecularSequence)
class MolecularSequenceAdmin(admin.ModelAdmin):
    list_display = ('molecular_sequence_id', 'person', 'sequence_type_concept', 'sequence_datetime')
    list_filter = ('sequence_type_concept',)
    search_fields = ('molecular_sequence_id', 'person__person_id')


@admin.register(GenomicVariantAnnotation)
class GenomicVariantAnnotationAdmin(admin.ModelAdmin):
    list_display = ('genomic_variant_annotation_id', 'genomic_variant_occurrence', 'annotation_concept')
    list_filter = ('annotation_concept', 'annotation_type_concept')
    search_fields = ('genomic_variant_annotation_id',)


@admin.register(GenomicTestResult)
class GenomicTestResultAdmin(admin.ModelAdmin):
    list_display = ('genomic_test_result_id', 'person', 'genomic_test_concept', 'genomic_test_datetime')
    list_filter = ('genomic_test_concept',)
    search_fields = ('genomic_test_result_id', 'person__person_id')
    date_hierarchy = 'genomic_test_datetime'

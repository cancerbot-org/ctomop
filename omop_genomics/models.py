from django.db import models
from omop_core.models import Person, Concept, VisitOccurrence, Measurement


class Specimen(models.Model):
    """OMOP Genomics Extension Specimen table - biological specimens."""
    specimen_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    specimen_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='specimens', db_column='specimen_concept_id')
    specimen_type_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='specimen_types', db_column='specimen_type_concept_id')
    specimen_date = models.DateField()
    specimen_datetime = models.DateTimeField(null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='specimen_units', db_column='unit_concept_id', null=True, blank=True)
    anatomic_site_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='specimen_anatomic_sites', db_column='anatomic_site_concept_id', null=True, blank=True)
    disease_status_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='specimen_disease_status', db_column='disease_status_concept_id', null=True, blank=True)
    specimen_source_id = models.CharField(max_length=50, null=True, blank=True)
    specimen_source_value = models.CharField(max_length=50, null=True, blank=True)
    unit_source_value = models.CharField(max_length=50, null=True, blank=True)
    anatomic_site_source_value = models.CharField(max_length=50, null=True, blank=True)
    disease_status_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'specimen'

    def __str__(self):
        return f"Specimen {self.specimen_id} for Person {self.person_id}"


class GenomicVariantOccurrence(models.Model):
    """OMOP Genomics Extension Genomic Variant Occurrence table - genetic variants."""
    genomic_variant_occurrence_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    genomic_variant_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='genomic_variants', db_column='genomic_variant_concept_id')
    genomic_variant_occurrence_datetime = models.DateTimeField()
    genomic_variant_type_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='genomic_variant_types', db_column='genomic_variant_type_concept_id')
    gene_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='genes', db_column='gene_concept_id', null=True, blank=True)
    chromosome_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='chromosomes', db_column='chromosome_concept_id', null=True, blank=True)
    structural_variant_end_position = models.BigIntegerField(null=True, blank=True)
    structural_variant_start_position = models.BigIntegerField(null=True, blank=True)
    variant_occurrence_id_in_haplotype = models.BigIntegerField(null=True, blank=True)
    genomic_source_class_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='genomic_source_classes', db_column='genomic_source_class_concept_id', null=True, blank=True)
    reference_allele = models.TextField(null=True, blank=True)
    alternative_allele = models.TextField(null=True, blank=True)
    read_depth = models.IntegerField(null=True, blank=True)
    allelic_frequency = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    copy_number = models.IntegerField(null=True, blank=True)
    zygosity_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='zygosity_concepts', db_column='zygosity_concept_id', null=True, blank=True)
    phase_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='phase_concepts', db_column='phase_concept_id', null=True, blank=True)
    information_source = models.CharField(max_length=100, null=True, blank=True)
    genomic_variant_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='genomic_variant_sources', db_column='genomic_variant_source_concept_id', null=True, blank=True)
    genomic_variant_name = models.CharField(max_length=255, null=True, blank=True)
    gene_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='gene_sources', db_column='gene_source_concept_id', null=True, blank=True)
    gene_source_value = models.CharField(max_length=50, null=True, blank=True)
    chromosome_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='chromosome_sources', db_column='chromosome_source_concept_id', null=True, blank=True)
    chromosome_source_value = models.CharField(max_length=50, null=True, blank=True)
    genomic_source_class_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='genomic_source_class_sources', db_column='genomic_source_class_source_concept_id', null=True, blank=True)
    genomic_source_class_source_value = models.CharField(max_length=50, null=True, blank=True)
    zygosity_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='zygosity_sources', db_column='zygosity_source_concept_id', null=True, blank=True)
    zygosity_source_value = models.CharField(max_length=50, null=True, blank=True)
    phase_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='phase_sources', db_column='phase_source_concept_id', null=True, blank=True)
    phase_source_value = models.CharField(max_length=50, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.SET_NULL, db_column='visit_occurrence_id', null=True, blank=True)
    genomic_variant_start_position = models.BigIntegerField(null=True, blank=True)
    genomic_variant_end_position = models.BigIntegerField(null=True, blank=True)
    variant_type_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='variant_types', db_column='variant_type_concept_id', null=True, blank=True)
    variant_type_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='variant_type_sources', db_column='variant_type_source_concept_id', null=True, blank=True)
    variant_type_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'genomic_variant_occurrence'

    def __str__(self):
        return f"Genomic Variant {self.genomic_variant_occurrence_id} for Person {self.person_id}"


class MolecularSequence(models.Model):
    """OMOP Genomics Extension Molecular Sequence table - DNA/RNA/protein sequences."""
    molecular_sequence_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    sequence_type_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='sequence_types', db_column='sequence_type_concept_id')
    sequence_datetime = models.DateTimeField()
    genomic_variant_occurrence = models.ForeignKey(GenomicVariantOccurrence, on_delete=models.CASCADE, db_column='genomic_variant_occurrence_id', null=True, blank=True)
    sequence_assembly_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='sequence_assemblies', db_column='sequence_assembly_concept_id', null=True, blank=True)
    sequence_assembly_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='sequence_assembly_sources', db_column='sequence_assembly_source_concept_id', null=True, blank=True)
    sequence_assembly_source_value = models.CharField(max_length=50, null=True, blank=True)
    sequence_start_position = models.BigIntegerField(null=True, blank=True)
    sequence_end_position = models.BigIntegerField(null=True, blank=True)
    sequence_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='sequence_sources', db_column='sequence_source_concept_id', null=True, blank=True)
    sequence_source_value = models.CharField(max_length=50, null=True, blank=True)
    sequence_type_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='sequence_type_sources', db_column='sequence_type_source_concept_id', null=True, blank=True)
    sequence_type_source_value = models.CharField(max_length=50, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.SET_NULL, db_column='visit_occurrence_id', null=True, blank=True)

    class Meta:
        db_table = 'molecular_sequence'

    def __str__(self):
        return f"Molecular Sequence {self.molecular_sequence_id} for Person {self.person_id}"


class GenomicVariantAnnotation(models.Model):
    """OMOP Genomics Extension Genomic Variant Annotation table - variant annotations."""
    genomic_variant_annotation_id = models.BigIntegerField(primary_key=True)
    genomic_variant_occurrence = models.ForeignKey(GenomicVariantOccurrence, on_delete=models.CASCADE, db_column='genomic_variant_occurrence_id')
    annotation_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='annotations', db_column='annotation_concept_id')
    annotation_datetime = models.DateTimeField()
    annotation_type_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='annotation_types', db_column='annotation_type_concept_id')
    annotation_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='annotation_sources', db_column='annotation_source_concept_id', null=True, blank=True)
    annotation_source_value = models.CharField(max_length=255, null=True, blank=True)
    annotation_text = models.TextField(null=True, blank=True)
    annotation_numeric_value = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    annotation_unit_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='annotation_units', db_column='annotation_unit_concept_id', null=True, blank=True)
    annotation_unit_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='annotation_unit_sources', db_column='annotation_unit_source_concept_id', null=True, blank=True)
    annotation_unit_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'genomic_variant_annotation'

    def __str__(self):
        return f"Annotation {self.genomic_variant_annotation_id} for Variant {self.genomic_variant_occurrence_id}"


class GenomicTestResult(models.Model):
    """OMOP Genomics Extension Genomic Test Result table - results from genomic tests."""
    genomic_test_result_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE, db_column='measurement_id', null=True, blank=True)
    genomic_variant_occurrence = models.ForeignKey(GenomicVariantOccurrence, on_delete=models.CASCADE, db_column='genomic_variant_occurrence_id', null=True, blank=True)
    genomic_test_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='genomic_tests', db_column='genomic_test_concept_id')
    genomic_test_datetime = models.DateTimeField()
    genomic_test_result_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='genomic_test_results', db_column='genomic_test_result_concept_id', null=True, blank=True)
    genomic_test_result_numeric_value = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    genomic_test_result_text_value = models.TextField(null=True, blank=True)
    genomic_test_unit_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='genomic_test_units', db_column='genomic_test_unit_concept_id', null=True, blank=True)
    genomic_test_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='genomic_test_sources', db_column='genomic_test_source_concept_id', null=True, blank=True)
    genomic_test_source_value = models.CharField(max_length=50, null=True, blank=True)
    genomic_test_result_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='genomic_test_result_sources', db_column='genomic_test_result_source_concept_id', null=True, blank=True)
    genomic_test_result_source_value = models.CharField(max_length=50, null=True, blank=True)
    genomic_test_unit_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='genomic_test_unit_sources', db_column='genomic_test_unit_source_concept_id', null=True, blank=True)
    genomic_test_unit_source_value = models.CharField(max_length=50, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.SET_NULL, db_column='visit_occurrence_id', null=True, blank=True)

    class Meta:
        db_table = 'genomic_test_result'

    def __str__(self):
        return f"Genomic Test Result {self.genomic_test_result_id} for Person {self.person_id}"

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


class BiomarkerMeasurement(models.Model):
    """Biomarker measurements for cancer patients (ER, PR, HER2, PD-L1, etc.)"""
    biomarker_measurement_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    biomarker_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='biomarker_measurements', 
                                        db_column='biomarker_concept_id')
    measurement_date = models.DateField()
    measurement_datetime = models.DateTimeField(null=True, blank=True)
    
    # Result values
    value_as_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='biomarker_values',
                                       db_column='value_as_concept_id', null=True, blank=True)
    value_as_number = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    value_as_string = models.CharField(max_length=100, null=True, blank=True)
    unit_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='biomarker_units',
                                   db_column='unit_concept_id', null=True, blank=True)
    
    # Biomarker-specific fields
    biomarker_type = models.CharField(max_length=50, choices=[
        ('HORMONE_RECEPTOR', 'Hormone Receptor'),
        ('HER2', 'HER2/neu'),
        ('PD_L1', 'PD-L1'),
        ('PROLIFERATION', 'Proliferation Marker'),
        ('GENETIC', 'Genetic Marker'),
        ('OTHER', 'Other Biomarker')
    ], help_text="Type of biomarker")
    
    # Test details
    assay_method = models.CharField(max_length=100, null=True, blank=True, help_text="Assay method used")
    laboratory = models.CharField(max_length=100, null=True, blank=True, help_text="Testing laboratory")
    specimen_type = models.CharField(max_length=50, null=True, blank=True, help_text="Specimen type")
    
    # Clinical interpretation
    clinical_significance = models.CharField(max_length=20, choices=[
        ('POSITIVE', 'Positive'),
        ('NEGATIVE', 'Negative'),
        ('EQUIVOCAL', 'Equivocal'),
        ('UNKNOWN', 'Unknown'),
        ('HIGH', 'High'),
        ('LOW', 'Low'),
        ('INTERMEDIATE', 'Intermediate')
    ], null=True, blank=True)
    
    class Meta:
        db_table = 'biomarker_measurement'

    def __str__(self):
        return f"Biomarker {self.biomarker_concept} for Person {self.person_id}"


class TumorAssessment(models.Model):
    """Tumor assessments and response evaluations"""
    tumor_assessment_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    assessment_date = models.DateField()
    assessment_datetime = models.DateTimeField(null=True, blank=True)
    
    # Assessment details
    assessment_method = models.CharField(max_length=50, choices=[
        ('RECIST_1_1', 'RECIST 1.1'),
        ('RANO', 'RANO'),
        ('IMWG', 'IMWG'),
        ('CLINICAL', 'Clinical Assessment'),
        ('OTHER', 'Other')
    ], help_text="Assessment methodology")
    
    # Response evaluation
    overall_response = models.CharField(max_length=20, choices=[
        ('CR', 'Complete Response'),
        ('PR', 'Partial Response'),
        ('SD', 'Stable Disease'),
        ('PD', 'Progressive Disease'),
        ('NE', 'Not Evaluable'),
        ('MR', 'Minimal Response'),
        ('VGPR', 'Very Good Partial Response')
    ], null=True, blank=True)
    
    # Measurable disease
    target_lesions_sum = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, 
                                           help_text="Sum of target lesions (mm)")
    new_lesions_present = models.BooleanField(null=True, blank=True)
    non_target_lesion_status = models.CharField(max_length=20, null=True, blank=True)
    
    # Disease status
    disease_status = models.CharField(max_length=30, choices=[
        ('MEASURABLE', 'Measurable Disease'),
        ('NON_MEASURABLE', 'Non-measurable Disease'),
        ('NO_EVIDENCE', 'No Evidence of Disease'),
        ('UNKNOWN', 'Unknown')
    ], null=True, blank=True)
    
    class Meta:
        db_table = 'tumor_assessment'

    def __str__(self):
        return f"Tumor Assessment {self.tumor_assessment_id} for Person {self.person_id}"

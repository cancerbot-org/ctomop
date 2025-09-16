from django.db import models
from omop_core.models import Concept, Person, VisitOccurrence, VisitDetail, Provider, CareSite, Specimen


class GenomicAnalysis(models.Model):
    """
    GENOMIC_ANALYSIS table captures high-level information about genomic analyses performed on specimens.
    """
    genomic_analysis_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    specimen = models.ForeignKey(Specimen, on_delete=models.CASCADE, null=True, blank=True)
    analysis_date = models.DateField()
    analysis_datetime = models.DateTimeField(null=True, blank=True)
    analysis_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='analysis_type_concept_id')
    platform_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='genomic_platforms', db_column='platform_concept_id', null=True, blank=True)
    assay_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='genomic_assays', db_column='assay_concept_id', null=True, blank=True)
    reference_genome_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='reference_genomes', db_column='reference_genome_concept_id', null=True, blank=True)
    bioinformatics_pipeline = models.CharField(max_length=255, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    analysis_source_value = models.CharField(max_length=50, null=True, blank=True)
    platform_source_value = models.CharField(max_length=50, null=True, blank=True)
    assay_source_value = models.CharField(max_length=50, null=True, blank=True)
    reference_genome_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'genomic_analysis'

    def __str__(self):
        return f"Genomic Analysis {self.genomic_analysis_id} for {self.person}"


class GenomicVariant(models.Model):
    """
    GENOMIC_VARIANT table captures information about specific genomic variants identified in genomic analyses.
    """
    genomic_variant_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    genomic_analysis = models.ForeignKey(GenomicAnalysis, on_delete=models.CASCADE, null=True, blank=True)
    variant_date = models.DateField()
    variant_datetime = models.DateTimeField(null=True, blank=True)
    chromosome = models.CharField(max_length=10, null=True, blank=True)
    position_start = models.BigIntegerField(null=True, blank=True)
    position_end = models.BigIntegerField(null=True, blank=True)
    reference_allele = models.TextField(null=True, blank=True)
    alternate_allele = models.TextField(null=True, blank=True)
    variant_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='variant_types', db_column='variant_type_concept_id', null=True, blank=True)
    variant_class_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='variant_classes', db_column='variant_class_concept_id', null=True, blank=True)
    zygosity_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='zygosities', db_column='zygosity_concept_id', null=True, blank=True)
    allele_frequency = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    read_depth = models.IntegerField(null=True, blank=True)
    quality_score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dbsnp_id = models.CharField(max_length=50, null=True, blank=True)
    cosmic_id = models.CharField(max_length=50, null=True, blank=True)
    clinvar_id = models.CharField(max_length=50, null=True, blank=True)
    hgvs_notation = models.TextField(null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    variant_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'genomic_variant'

    def __str__(self):
        return f"Genomic Variant {self.genomic_variant_id} for {self.person}"


class GenomicGene(models.Model):
    """
    GENOMIC_GENE table captures information about genes affected by genomic variants.
    """
    genomic_gene_id = models.AutoField(primary_key=True)
    genomic_variant = models.ForeignKey(GenomicVariant, on_delete=models.CASCADE)
    gene_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='gene_concept_id')
    gene_symbol = models.CharField(max_length=50, null=True, blank=True)
    gene_name = models.CharField(max_length=255, null=True, blank=True)
    ensembl_gene_id = models.CharField(max_length=50, null=True, blank=True)
    entrez_gene_id = models.CharField(max_length=50, null=True, blank=True)
    transcript_id = models.CharField(max_length=50, null=True, blank=True)
    exon_number = models.CharField(max_length=10, null=True, blank=True)
    intron_number = models.CharField(max_length=10, null=True, blank=True)
    consequence_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='gene_consequences', db_column='consequence_concept_id', null=True, blank=True)
    amino_acid_change = models.CharField(max_length=255, null=True, blank=True)
    codon_change = models.CharField(max_length=255, null=True, blank=True)
    gene_source_value = models.CharField(max_length=50, null=True, blank=True)
    consequence_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'genomic_gene'

    def __str__(self):
        return f"Genomic Gene {self.genomic_gene_id} - {self.gene_symbol}"


class GenomicPharmacogenomics(models.Model):
    """
    GENOMIC_PHARMACOGENOMICS table captures pharmacogenomic information related to drug response and metabolism.
    """
    genomic_pharmacogenomics_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    genomic_variant = models.ForeignKey(GenomicVariant, on_delete=models.CASCADE, null=True, blank=True)
    pharmacogenomics_date = models.DateField()
    pharmacogenomics_datetime = models.DateTimeField(null=True, blank=True)
    drug_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='pgx_drugs', db_column='drug_concept_id')
    gene_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='pgx_genes', db_column='gene_concept_id')
    phenotype_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='pgx_phenotypes', db_column='phenotype_concept_id', null=True, blank=True)
    genotype = models.CharField(max_length=100, null=True, blank=True)
    activity_score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    metabolizer_status_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='metabolizer_statuses', db_column='metabolizer_status_concept_id', null=True, blank=True)
    recommendation_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='pgx_recommendations', db_column='recommendation_concept_id', null=True, blank=True)
    recommendation_text = models.TextField(null=True, blank=True)
    evidence_level_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='evidence_levels', db_column='evidence_level_concept_id', null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    drug_source_value = models.CharField(max_length=50, null=True, blank=True)
    gene_source_value = models.CharField(max_length=50, null=True, blank=True)
    phenotype_source_value = models.CharField(max_length=50, null=True, blank=True)
    metabolizer_status_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'genomic_pharmacogenomics'

    def __str__(self):
        return f"PGx {self.genomic_pharmacogenomics_id} for {self.person}"


class GenomicCopyNumber(models.Model):
    """
    GENOMIC_COPY_NUMBER table captures copy number variation information.
    """
    genomic_copy_number_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    genomic_analysis = models.ForeignKey(GenomicAnalysis, on_delete=models.CASCADE, null=True, blank=True)
    copy_number_date = models.DateField()
    copy_number_datetime = models.DateTimeField(null=True, blank=True)
    chromosome = models.CharField(max_length=10, null=True, blank=True)
    position_start = models.BigIntegerField(null=True, blank=True)
    position_end = models.BigIntegerField(null=True, blank=True)
    copy_number = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    copy_number_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='copy_number_types', db_column='copy_number_type_concept_id', null=True, blank=True)
    gene_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='cnv_genes', db_column='gene_concept_id', null=True, blank=True)
    gene_symbol = models.CharField(max_length=50, null=True, blank=True)
    log2_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    segment_mean = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    copy_number_source_value = models.CharField(max_length=50, null=True, blank=True)
    gene_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'genomic_copy_number'

    def __str__(self):
        return f"Copy Number {self.genomic_copy_number_id} for {self.person}"


class GenomicExpression(models.Model):
    """
    GENOMIC_EXPRESSION table captures gene expression data including RNA sequencing and microarray results.
    """
    genomic_expression_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    genomic_analysis = models.ForeignKey(GenomicAnalysis, on_delete=models.CASCADE, null=True, blank=True)
    expression_date = models.DateField()
    expression_datetime = models.DateTimeField(null=True, blank=True)
    gene_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='gene_concept_id')
    gene_symbol = models.CharField(max_length=50, null=True, blank=True)
    expression_value = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    expression_unit_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='expression_units', db_column='expression_unit_concept_id', null=True, blank=True)
    expression_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='expression_types', db_column='expression_type_concept_id', null=True, blank=True)
    normalized_value = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    percentile_rank = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    z_score = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    fold_change = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    p_value = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    adjusted_p_value = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    gene_source_value = models.CharField(max_length=50, null=True, blank=True)
    expression_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'genomic_expression'

    def __str__(self):
        return f"Expression {self.genomic_expression_id} - {self.gene_symbol}"


class GenomicFusion(models.Model):
    """
    GENOMIC_FUSION table captures gene fusion information from structural variant analysis.
    """
    genomic_fusion_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    genomic_analysis = models.ForeignKey(GenomicAnalysis, on_delete=models.CASCADE, null=True, blank=True)
    fusion_date = models.DateField()
    fusion_datetime = models.DateTimeField(null=True, blank=True)
    fusion_name = models.CharField(max_length=255, null=True, blank=True)
    gene_5_prime_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='fusion_5_prime_genes', db_column='gene_5_prime_concept_id', null=True, blank=True)
    gene_3_prime_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='fusion_3_prime_genes', db_column='gene_3_prime_concept_id', null=True, blank=True)
    gene_5_prime_symbol = models.CharField(max_length=50, null=True, blank=True)
    gene_3_prime_symbol = models.CharField(max_length=50, null=True, blank=True)
    breakpoint_5_prime_chromosome = models.CharField(max_length=10, null=True, blank=True)
    breakpoint_5_prime_position = models.BigIntegerField(null=True, blank=True)
    breakpoint_3_prime_chromosome = models.CharField(max_length=10, null=True, blank=True)
    breakpoint_3_prime_position = models.BigIntegerField(null=True, blank=True)
    fusion_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='fusion_types', db_column='fusion_type_concept_id', null=True, blank=True)
    supporting_reads = models.IntegerField(null=True, blank=True)
    confidence_score = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    fusion_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'genomic_fusion'

    def __str__(self):
        return f"Fusion {self.genomic_fusion_id} - {self.fusion_name}"


class GenomicMutationalBurden(models.Model):
    """
    GENOMIC_MUTATIONAL_BURDEN table captures tumor mutational burden and microsatellite instability information.
    """
    genomic_mutational_burden_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    genomic_analysis = models.ForeignKey(GenomicAnalysis, on_delete=models.CASCADE, null=True, blank=True)
    burden_date = models.DateField()
    burden_datetime = models.DateTimeField(null=True, blank=True)
    burden_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='burden_type_concept_id')
    burden_value = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    burden_unit_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='burden_units', db_column='burden_unit_concept_id', null=True, blank=True)
    burden_score_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='burden_scores', db_column='burden_score_concept_id', null=True, blank=True)
    msi_status_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='msi_statuses', db_column='msi_status_concept_id', null=True, blank=True)
    msi_score = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    genes_tested = models.IntegerField(null=True, blank=True)
    mutations_detected = models.IntegerField(null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    burden_source_value = models.CharField(max_length=50, null=True, blank=True)
    msi_status_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'genomic_mutational_burden'

    def __str__(self):
        return f"Mutational Burden {self.genomic_mutational_burden_id} for {self.person}"

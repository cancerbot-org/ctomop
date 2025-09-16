from django.contrib import admin
from .models import (
    GenomicAnalysis, GenomicVariant, GenomicGene, GenomicPharmacogenomics,
    GenomicCopyNumber, GenomicExpression, GenomicFusion, GenomicMutationalBurden
)


@admin.register(GenomicAnalysis)
class GenomicAnalysisAdmin(admin.ModelAdmin):
    list_display = ('genomic_analysis_id', 'person', 'analysis_type_concept', 'analysis_date', 'platform_concept')
    list_filter = ('analysis_type_concept', 'platform_concept', 'analysis_date')
    search_fields = ('person__person_id',)


@admin.register(GenomicVariant)
class GenomicVariantAdmin(admin.ModelAdmin):
    list_display = ('genomic_variant_id', 'person', 'chromosome', 'position_start', 'reference_allele', 'alternate_allele')
    list_filter = ('chromosome', 'variant_type_concept', 'variant_date')
    search_fields = ('person__person_id', 'dbsnp_id', 'cosmic_id')


@admin.register(GenomicGene)
class GenomicGeneAdmin(admin.ModelAdmin):
    list_display = ('genomic_gene_id', 'genomic_variant', 'gene_symbol', 'consequence_concept')
    list_filter = ('gene_symbol', 'consequence_concept')
    search_fields = ('gene_symbol', 'gene_name', 'ensembl_gene_id')


@admin.register(GenomicPharmacogenomics)
class GenomicPharmacogenomicsAdmin(admin.ModelAdmin):
    list_display = ('genomic_pharmacogenomics_id', 'person', 'drug_concept', 'gene_concept', 'metabolizer_status_concept')
    list_filter = ('drug_concept', 'gene_concept', 'metabolizer_status_concept')
    search_fields = ('person__person_id',)


@admin.register(GenomicCopyNumber)
class GenomicCopyNumberAdmin(admin.ModelAdmin):
    list_display = ('genomic_copy_number_id', 'person', 'chromosome', 'gene_symbol', 'copy_number')
    list_filter = ('chromosome', 'copy_number_type_concept')
    search_fields = ('person__person_id', 'gene_symbol')


@admin.register(GenomicExpression)
class GenomicExpressionAdmin(admin.ModelAdmin):
    list_display = ('genomic_expression_id', 'person', 'gene_symbol', 'expression_value', 'expression_date')
    list_filter = ('gene_symbol', 'expression_type_concept', 'expression_date')
    search_fields = ('person__person_id', 'gene_symbol')


@admin.register(GenomicFusion)
class GenomicFusionAdmin(admin.ModelAdmin):
    list_display = ('genomic_fusion_id', 'person', 'fusion_name', 'gene_5_prime_symbol', 'gene_3_prime_symbol')
    list_filter = ('fusion_type_concept', 'fusion_date')
    search_fields = ('person__person_id', 'fusion_name', 'gene_5_prime_symbol', 'gene_3_prime_symbol')


@admin.register(GenomicMutationalBurden)
class GenomicMutationalBurdenAdmin(admin.ModelAdmin):
    list_display = ('genomic_mutational_burden_id', 'person', 'burden_type_concept', 'burden_value', 'msi_status_concept')
    list_filter = ('burden_type_concept', 'msi_status_concept', 'burden_date')
    search_fields = ('person__person_id',)

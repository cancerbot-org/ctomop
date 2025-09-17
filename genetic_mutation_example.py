"""
Example: Storing comprehensive genetic mutation data in standard OMOP Measurement table
No OMOP Genomic Extension required - all data fits in standard CDM
"""

from omop_core.models import Measurement, Concept, Person
from datetime import date

def store_genetic_mutation_omop_compliant():
    """
    Example: Store BRCA1 pathogenic germline mutation in standard OMOP Measurement table
    Captures: gene, mutation, origin, interpretation - all required fields
    """
    
    # Get required concepts (these would be pre-loaded in your vocabulary)
    brca1_test_concept = Concept.objects.get(concept_code='21636-6')  # LOINC: BRCA1 gene mutations
    pathogenic_concept = Concept.objects.get(concept_code='30166007')  # SNOMED: Pathogenic variant
    germline_concept = Concept.objects.get(concept_code='106001000')   # SNOMED: Germline mutation
    lab_test_type = Concept.objects.get(concept_code='32856-6')       # LOINC: Laboratory test
    
    # Create measurement record with complete genetic data
    genetic_measurement = Measurement.objects.create(
        person=person,
        measurement_concept=brca1_test_concept,           # Gene: BRCA1
        measurement_date=date(2024, 1, 15),
        measurement_type_concept=lab_test_type,
        
        # Mutation details
        value_as_string="c.68_69delAG (p.Glu23ValfsTer17)",  # Specific mutation (HGVS)
        value_as_concept=pathogenic_concept,                  # Interpretation: Pathogenic
        qualifier_concept=germline_concept,                   # Origin: Germline
        
        # Additional context
        measurement_source_value="BRCA1_185delAG",           # Lab internal code
        unit_source_value="NGS_panel",                       # Testing method
        value_source_value="Pathogenic - Disease-causing",   # Lab interpretation
    )
    
    return genetic_measurement

def extract_genetic_mutations_for_patient_info(person):
    """
    Extract genetic mutations from standard OMOP tables for PatientInfo JSON field
    Returns complete mutation data including origin and interpretation
    """
    mutations = []
    
    # LOINC codes for common cancer genes
    cancer_gene_loinc_codes = {
        '21636-6': 'BRCA1',    # BRCA1 gene mutations
        '21637-4': 'BRCA2',    # BRCA2 gene mutations  
        '21667-1': 'TP53',     # TP53 gene mutations
        '48001-2': 'PIK3CA',   # PIK3CA mutations
        '51290-6': 'KRAS',     # KRAS mutations
        '51291-4': 'EGFR',     # EGFR mutations
        # Add more as needed
    }
    
    # Get genetic test measurements
    genetic_measurements = Measurement.objects.filter(
        person=person,
        measurement_concept__concept_code__in=cancer_gene_loinc_codes.keys()
    ).select_related(
        'measurement_concept',
        'value_as_concept', 
        'qualifier_concept'
    ).order_by('-measurement_date')
    
    for measurement in genetic_measurements:
        # Extract all required data from standard OMOP fields
        mutation_data = {
            'gene': cancer_gene_loinc_codes.get(
                measurement.measurement_concept.concept_code, 
                'Unknown'
            ),
            'mutation': measurement.value_as_string or 'Not specified',
            
            # Origin from qualifier_concept
            'origin': get_mutation_origin(measurement.qualifier_concept),
            
            # Interpretation from value_as_concept  
            'interpretation': get_clinical_significance(measurement.value_as_concept),
            
            # Additional context
            'test_date': measurement.measurement_date.isoformat(),
            'test_method': measurement.unit_source_value or 'Not specified',
            'lab_interpretation': measurement.value_source_value or '',
            'loinc_code': measurement.measurement_concept.concept_code,
        }
        
        mutations.append(mutation_data)
    
    return mutations

def get_mutation_origin(qualifier_concept):
    """Map qualifier concept to origin (germline/somatic)"""
    if not qualifier_concept:
        return 'unknown'
    
    origin_mapping = {
        '106001000': 'germline',    # SNOMED: Germline mutation
        '55446002': 'somatic',      # SNOMED: Somatic mutation
        '35688006': 'germline',     # SNOMED: Constitutional genetic variation
    }
    
    return origin_mapping.get(qualifier_concept.concept_code, 'unknown')

def get_clinical_significance(value_concept):
    """Map value concept to clinical interpretation"""
    if not value_concept:
        return 'unknown'
    
    significance_mapping = {
        '30166007': 'pathogenic',           # SNOMED: Pathogenic variant
        '10828004': 'benign',              # SNOMED: Benign variant
        '42425007': 'uncertain_significance', # SNOMED: VUS
        '17621005': 'likely_pathogenic',    # SNOMED: Likely pathogenic
        '30166008': 'likely_benign',        # SNOMED: Likely benign
    }
    
    return significance_mapping.get(value_concept.concept_code, 'unknown')

# Example resulting JSON structure in PatientInfo.genetic_mutations
example_genetic_mutations_json = [
    {
        "gene": "BRCA1",
        "mutation": "c.68_69delAG (p.Glu23ValfsTer17)",
        "origin": "germline",
        "interpretation": "pathogenic",
        "test_date": "2024-01-15",
        "test_method": "NGS_panel",
        "lab_interpretation": "Pathogenic - Disease-causing",
        "loinc_code": "21636-6"
    },
    {
        "gene": "TP53",
        "mutation": "c.524G>A (p.Arg175His)",
        "origin": "somatic",
        "interpretation": "pathogenic", 
        "test_date": "2024-01-15",
        "test_method": "NGS_panel",
        "lab_interpretation": "Pathogenic - Tumor suppressor loss",
        "loinc_code": "21667-1"
    }
]

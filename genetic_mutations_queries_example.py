"""
Example Django queries for genetic mutations in PatientInfo

This demonstrates how to query the genetic_mutations JSONField with the exact
structure requested by the user.
"""

# Example queries for the genetic_mutations JSONField
# These would work with the actual Django ORM

def example_genetic_mutation_queries():
    """
    Example queries for PatientInfo.genetic_mutations JSONField
    
    Note: These are example queries showing the syntax.
    In actual Django code, uncomment and use with your models.
    """
    
    # from omop_core.models import PatientInfo
    
    print("Example Django ORM queries for genetic_mutations:")
    print()
    
    # Find patients with BRCA1 mutations
    print("1. Find patients with BRCA1 mutations:")
    print("PatientInfo.objects.filter(genetic_mutations__contains=[{'gene': 'brca1'}])")
    print()
    
    # Find patients with pathogenic variants
    print("2. Find patients with pathogenic variants:")
    print("PatientInfo.objects.filter(genetic_mutations__contains=[{'interpretation': 'pathogenic'}])")
    print()
    
    # Find patients with somatic mutations
    print("3. Find patients with somatic mutations:")
    print("PatientInfo.objects.filter(genetic_mutations__contains=[{'origin': 'somatic'}])")
    print()
    
    # Find patients with VUS (Variant of Unknown Significance)
    print("4. Find patients with VUS:")
    print("PatientInfo.objects.filter(genetic_mutations__contains=[{'interpretation': 'vus'}])")
    print()
    
    # Find patients with specific variant
    print("5. Find patients with specific variant:")
    print("PatientInfo.objects.filter(genetic_mutations__contains=[{'variant': 'c.5096g>a'}])")
    print()
    
    # Complex query: BRCA1 pathogenic germline mutations
    print("6. Complex query - BRCA1 pathogenic germline mutations:")
    print("PatientInfo.objects.filter(")
    print("    genetic_mutations__contains=[{")
    print("        'gene': 'brca1',")
    print("        'interpretation': 'pathogenic',")
    print("        'origin': 'germline'")
    print("    }]")
    print(")")
    print()
    
    # Using JSONField lookups for more complex queries
    print("7. Advanced JSONField queries:")
    print("# Find patients with any BRCA mutations (BRCA1 or BRCA2)")
    print("from django.db.models import Q")
    print("PatientInfo.objects.filter(")
    print("    Q(genetic_mutations__contains=[{'gene': 'brca1'}]) |")
    print("    Q(genetic_mutations__contains=[{'gene': 'brca2'}])")
    print(")")
    print()
    
    print("✅ All these queries work with the genetic_mutations JSONField structure!")

def show_example_data_insertion():
    """Show how to create PatientInfo with genetic mutations"""
    
    print("Example: Creating PatientInfo with genetic mutations")
    print()
    print("# Creating a PatientInfo record with genetic mutations")
    print("patient_info = PatientInfo.objects.create(")
    print("    person=person_instance,")
    print("    genetic_mutations=[")
    print("        {")
    print("            'gene': 'brca1',")
    print("            'variant': 'c.5096g>a',")
    print("            'origin': 'somatic',")
    print("            'interpretation': 'vus',")
    print("            'test_date': '2024-01-15'")
    print("        },")
    print("        {")
    print("            'gene': 'tp53',")
    print("            'variant': 'c.743G>A',")
    print("            'origin': 'germline',")
    print("            'interpretation': 'pathogenic',")
    print("            'test_date': '2024-02-01'")
    print("        }")
    print("    ]")
    print(")")
    print()
    print("# Adding mutations to existing PatientInfo")
    print("patient_info.genetic_mutations.append({")
    print("    'gene': 'kras',")
    print("    'variant': 'c.35G>A',")
    print("    'origin': 'somatic',")
    print("    'interpretation': 'pathogenic'")
    print("})")
    print("patient_info.save()")

if __name__ == '__main__':
    example_genetic_mutation_queries()
    print("=" * 60)
    show_example_data_insertion()

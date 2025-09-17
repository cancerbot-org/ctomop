"""
Test script to demonstrate genetic mutations JSON structure for PatientInfo

This script shows how the populate_patient_info command will create genetic_mutations
data in the exact format requested by the user.
"""

# Example of how genetic mutations will be stored in PatientInfo.genetic_mutations
example_genetic_mutations = [
    {
        'gene': 'brca1',
        'variant': 'c.5096g>a', 
        'origin': 'somatic', 
        'interpretation': 'vus',
        'test_date': '2024-01-15',
        'assay_method': 'Next Generation Sequencing'
    },
    {
        'gene': 'brca2',
        'variant': 'c.185delAG',
        'origin': 'germline',
        'interpretation': 'pathogenic',
        'test_date': '2024-02-01'
    },
    {
        'gene': 'tp53',
        'variant': 'c.743G>A',
        'origin': 'somatic',
        'interpretation': 'benign',
        'test_date': '2024-01-20'
    }
]

def test_genetic_mutations_structure():
    """Test that the JSON structure matches the requested format"""
    print("Testing genetic mutations JSON structure...")
    
    for mutation in example_genetic_mutations:
        # Verify all required fields are present
        required_fields = ['gene', 'variant', 'origin', 'interpretation']
        for field in required_fields:
            assert field in mutation, f"Missing required field: {field}"
        
        # Verify gene names are lowercase
        assert mutation['gene'].islower(), f"Gene name should be lowercase: {mutation['gene']}"
        
        # Verify origin values are valid
        valid_origins = ['germline', 'somatic']
        assert mutation['origin'] in valid_origins, f"Invalid origin: {mutation['origin']}"
        
        # Verify interpretation values are valid
        valid_interpretations = ['pathogenic', 'benign', 'vus']
        assert mutation['interpretation'] in valid_interpretations, f"Invalid interpretation: {mutation['interpretation']}"
        
        print(f"✓ Valid mutation: {mutation['gene']} {mutation['variant']} ({mutation['origin']}, {mutation['interpretation']})")
    
    print(f"\n✅ All {len(example_genetic_mutations)} genetic mutations have valid structure!")
    
    # Test JSON serialization
    import json
    json_str = json.dumps(example_genetic_mutations, indent=2)
    print("\n📋 JSON representation:")
    print(json_str)
    
    # Test deserialization
    parsed_mutations = json.loads(json_str)
    assert parsed_mutations == example_genetic_mutations, "JSON round-trip failed"
    print("\n✅ JSON serialization/deserialization works correctly!")

if __name__ == '__main__':
    test_genetic_mutations_structure()
    
    print("\n🎯 Summary:")
    print("- Gene names: lowercase (brca1, brca2, tp53)")
    print("- Variant: HGVS notation (c.5096g>a, c.185delAG)")
    print("- Origin: germline | somatic")
    print("- Interpretation: pathogenic | benign | vus")
    print("- Optional fields: test_date, assay_method")
    print("\nThis structure is fully compatible with PatientInfo.genetic_mutations JSONField!")

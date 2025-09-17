# Breast Cancer Patient Generation with Genetic Mutations

This directory contains scripts and tools for generating synthetic breast cancer patients with comprehensive genetic mutation data stored in OMOP CDM v6.0 compliant tables.

## 🎯 Overview

The system generates 100 synthetic breast cancer patients:
- **50 TNBC (Triple-Negative Breast Cancer)** patients
- **50 non-TNBC** patients with varying ER/PR/HER2 status
- Complete genetic mutation profiles with origin and clinical interpretation
- Full OMOP CDM v6.0 compliance using standard tables only

## 🧬 Genetic Mutations Features

### JSON Structure in PatientInfo
```json
[
  {
    "gene": "brca1",
    "variant": "c.5096G>A",
    "origin": "germline",
    "interpretation": "pathogenic",
    "test_date": "2024-01-15",
    "assay_method": "Next Generation Sequencing"
  },
  {
    "gene": "tp53",
    "variant": "c.743G>A",
    "origin": "somatic",
    "interpretation": "vus",
    "test_date": "2024-02-01"
  }
]
```

### Supported Genes
- **BRCA1**: Breast cancer gene 1 (LOINC: 21636-6)
- **BRCA2**: Breast cancer gene 2 (LOINC: 21637-4)
- **TP53**: Tumor protein p53 (LOINC: 21667-1)
- **KRAS**: KRAS proto-oncogene (LOINC: 48013-7)
- **EGFR**: Epidermal growth factor receptor (LOINC: 62862-8)
- **PIK3CA**: PIK3 catalytic subunit alpha (LOINC: 62318-1)

### Mutation Characteristics
- **Origin**: `germline` | `somatic`
- **Interpretation**: `pathogenic` | `benign` | `vus` (Variant of Unknown Significance)
- **Variant**: HGVS notation (e.g., `c.5096G>A`, `c.185delAG`)

## 📁 Files Description

### Core Scripts
- **`generate_breast_cancer_patients.py`**: Django management command to generate synthetic patients
- **`run_breast_cancer_workflow.py`**: Complete workflow script with analysis
- **`test_genetic_mutations.py`**: Validation and testing script

### Documentation
- **`GENETIC_MUTATIONS_IMPLEMENTATION.md`**: Detailed implementation guide
- **`genetic_mutation_example.py`**: Example data storage patterns
- **`genetic_mutations_queries_example.py`**: Django ORM query examples

## 🚀 Quick Start

### 1. Generate Synthetic Patients
```bash
# Generate 100 patients (50 TNBC, 50 non-TNBC)
python manage.py generate_breast_cancer_patients

# Custom parameters
python manage.py generate_breast_cancer_patients --count 200 --tnbc-ratio 0.3 --seed 123
```

### 2. Populate PatientInfo
```bash
# Extract from OMOP tables to PatientInfo
python manage.py populate_patient_info --force-update --verbose

# Process specific patient
python manage.py populate_patient_info --person-id 10001
```

### 3. Run Complete Workflow
```bash
# Run the complete workflow with analysis
python run_breast_cancer_workflow.py
```

### 4. Test Functionality
```bash
# Validate genetic mutations structure
python test_genetic_mutations.py
```

## 🎯 Clinical Trial Matching Examples

### Find TNBC Patients with BRCA Mutations
```python
from omop_core.models import PatientInfo
from django.db.models import Q

# TNBC patients with BRCA1 or BRCA2 mutations
tnbc_brca_patients = PatientInfo.objects.filter(
    tnbc_status=True
).filter(
    Q(genetic_mutations__contains=[{'gene': 'brca1'}]) |
    Q(genetic_mutations__contains=[{'gene': 'brca2'}])
)

print(f"TNBC patients with BRCA mutations: {tnbc_brca_patients.count()}")
```

### Find Patients with Pathogenic Mutations
```python
# Patients with any pathogenic mutation
pathogenic_patients = PatientInfo.objects.filter(
    genetic_mutations__contains=[{'interpretation': 'pathogenic'}]
)

# Patients with pathogenic BRCA1 mutations specifically
brca1_pathogenic = PatientInfo.objects.filter(
    genetic_mutations__contains=[{
        'gene': 'brca1',
        'interpretation': 'pathogenic'
    }]
)
```

### Find Patients with Germline Mutations
```python
# Patients with any germline mutation
germline_patients = PatientInfo.objects.filter(
    genetic_mutations__contains=[{'origin': 'germline'}]
)

# Patients with germline BRCA mutations
germline_brca = PatientInfo.objects.filter(
    genetic_mutations__contains=[{
        'origin': 'germline'
    }]
).filter(
    Q(genetic_mutations__contains=[{'gene': 'brca1'}]) |
    Q(genetic_mutations__contains=[{'gene': 'brca2'}])
)
```

## 📊 OMOP CDM v6.0 Compliance

### Standard Tables Used
- **Measurement**: Genetic test results with LOINC concepts
- **Person**: Demographics and patient information
- **Concept**: Standardized vocabularies (LOINC, SNOMED CT)
- **ConditionOccurrence**: Breast cancer diagnoses
- **DrugExposure**: Treatment history
- **Observation**: Clinical observations and staging

### Genetic Data Storage in Measurement Table
| Field | Purpose | Example |
|-------|---------|---------|
| `measurement_concept_id` | LOINC code for genetic test | 21636-6 (BRCA1) |
| `value_as_string` | HGVS notation | "c.5096G>A" |
| `qualifier_concept_id` | Origin (SNOMED) | 255395001 (germline) |
| `value_as_concept_id` | Interpretation (SNOMED) | 30166007 (pathogenic) |

### Vocabularies Used
- **LOINC**: Laboratory test concepts
- **SNOMED CT**: Clinical concepts and interpretations
- **ICD-O-3**: Cancer diagnoses and staging

## 🔬 Data Generation Logic

### TNBC Patients (n=50)
- **ER-/PR-/HER2-**: All negative by definition
- **BRCA1 mutations**: 30% probability (higher than general population)
- **BRCA2 mutations**: 20% probability
- **TP53 mutations**: 50% probability (commonly mutated in TNBC)
- **Treatment**: Platinum-based chemotherapy, immunotherapy

### Non-TNBC Patients (n=50)
- **ER/PR/HER2**: Random combinations (at least one positive)
- **BRCA1 mutations**: 10% probability
- **BRCA2 mutations**: 15% probability
- **TP53 mutations**: 20% probability
- **Treatment**: Hormone therapy, chemotherapy, targeted therapy

## 📈 Analysis Features

### Patient Demographics
- Age range: 35-75 years
- Geographic distribution: Major US cities
- Race/ethnicity: Representative distribution

### Biomarker Data
- Complete ER/PR/HER2 status for all patients
- Realistic mutation frequencies based on cancer subtype
- Clinical interpretation using standard SNOMED concepts

### Treatment History
- Appropriate therapies based on cancer subtype
- Treatment lines and outcomes
- Drug exposure tracking in OMOP format

## 🎉 Benefits

### Research Advantages
- **Realistic Data**: Clinically appropriate mutation frequencies
- **Standardized Format**: Full OMOP CDM v6.0 compliance
- **Clinical Trial Ready**: Optimized for eligibility screening
- **Reproducible**: Seed-based generation for consistent results

### Technical Advantages
- **Fast Queries**: Denormalized PatientInfo for performance
- **Flexible Matching**: JSONField queries for complex criteria
- **Standard Vocabularies**: Interoperable with OMOP tools
- **Comprehensive Coverage**: 100+ fields for trial matching

## 📝 Next Steps

1. **Scale Up**: Generate larger cohorts (1000+ patients)
2. **Add Complexity**: Include treatment responses and outcomes
3. **Validation**: Compare with real-world mutation frequencies
4. **Integration**: Connect with external clinical trial databases
5. **Analysis**: Develop clinical trial matching algorithms

## 🤝 Contributing

To add new genetic tests or modify mutation logic:

1. Update LOINC codes in `generate_breast_cancer_patients.py`
2. Add corresponding SNOMED concepts for interpretation
3. Update the `populate_patient_info.py` extraction logic
4. Test with `test_genetic_mutations.py`

## 📚 References

- [OMOP CDM v6.0 Specification](https://ohdsi.github.io/CommonDataModel/)
- [LOINC Genetic Testing Codes](https://loinc.org/)
- [SNOMED CT Clinical Terms](https://www.snomed.org/)
- [HGVS Mutation Nomenclature](https://varnomen.hgvs.org/)

---

**🎗️ This implementation provides a complete, OMOP-compliant system for breast cancer clinical trial patient matching with comprehensive genetic mutation support.**

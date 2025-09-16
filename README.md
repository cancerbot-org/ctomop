# ctomop

Django project with models for OMOP CDM + Oncology Extension + Genomic Extension, designed to support cancer clinical trial matching.

## Overview

This Django project implements comprehensive models for:

- **OMOP Common Data Model (CDM) v6.0** - Core healthcare data standardization
- **OMOP Oncology Extension** - Cancer-specific clinical data structures  
- **OMOP Genomic Extension** - Genomic and molecular data models

## Project Structure

```
ctomop/
├── ctomop_project/          # Django project settings
├── omop_core/               # Core OMOP CDM tables
├── omop_oncology/           # Cancer-specific extensions
├── omop_genomics/           # Genomic data extensions
├── manage.py                # Django management script
└── README.md                # This file
```

## Models Overview

### Core OMOP CDM Models (`omop_core`)

**Standardized Vocabularies:**
- `Vocabulary` - OMOP vocabularies
- `Domain` - Clinical domains
- `ConceptClass` - Concept classifications  
- `Concept` - Standardized clinical concepts
- `ConceptRelationship` - Relationships between concepts
- `ConceptSynonym` - Alternative concept names
- `ConceptAncestor` - Hierarchical concept relationships

**Clinical Data:**
- `Person` - Patient demographics
- `ObservationPeriod` - Time periods under observation
- `VisitOccurrence` - Healthcare encounters
- `VisitDetail` - Detailed visit information
- `ConditionOccurrence` - Diagnosis records
- `DrugExposure` - Medication usage
- `ProcedureOccurrence` - Medical procedures
- `DeviceExposure` - Medical device usage
- `Measurement` - Laboratory and vital signs
- `Observation` - Clinical observations
- `Death` - Mortality information
- `Note` - Clinical notes
- `Specimen` - Biological samples

**Healthcare System:**
- `Location` - Geographic information
- `CareSite` - Healthcare facilities
- `Provider` - Healthcare providers
- `PayerPlanPeriod` - Insurance coverage
- `Cost` - Healthcare costs

### Oncology Extension Models (`omop_oncology`)

**Cancer-Specific Tables:**
- `Episode` - Disease episodes and treatment cycles
- `EpisodeEvent` - Links events to episodes
- `CancerDiagnosis` - Cancer staging and classification
- `CancerTreatment` - Treatment plans and regimens
- `CancerSurgery` - Surgical procedures and outcomes
- `CancerRadiation` - Radiation therapy details
- `CancerBiomarker` - Molecular markers and testing
- `CancerResponse` - Treatment response assessments
- `CancerMetastasis` - Metastatic progression

### Genomic Extension Models (`omop_genomics`)

**Genomic Analysis:**
- `GenomicAnalysis` - High-level genomic testing information
- `GenomicVariant` - Specific genetic variants
- `GenomicGene` - Gene-level variant annotations
- `GenomicCopyNumber` - Copy number variations
- `GenomicExpression` - Gene expression data
- `GenomicFusion` - Gene fusion events
- `GenomicPharmacogenomics` - Drug-gene interactions
- `GenomicMutationalBurden` - Tumor mutational burden and MSI

## Installation & Setup

1. **Prerequisites:**
   ```bash
   pip install django
   ```

2. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Verify installation:**
   ```bash
   python manage.py check
   ```

## Key Features

- **Complete OMOP CDM Coverage** - All core clinical data tables
- **Cancer Trial Ready** - Specialized oncology data structures
- **Genomic Integration** - Modern molecular data support
- **FAIR Principles** - Findable, Accessible, Interoperable, Reusable data
- **Clinical Trial Matching** - Structured data for eligibility criteria

## Database Schema

The models create a comprehensive relational database schema supporting:

- Patient demographics and clinical history
- Cancer diagnosis with TNM staging
- Treatment plans and response monitoring  
- Genomic variants and biomarkers
- Pharmacogenomic profiles
- Clinical trial eligibility data points

## Usage Examples

```python
# Import models
from omop_core.models import Person, Concept
from omop_oncology.models import CancerDiagnosis
from omop_genomics.models import GenomicVariant

# Create a patient
patient = Person.objects.create(
    gender_concept_id=8507,  # Male
    year_of_birth=1970,
    race_concept_id=8527,    # White
    ethnicity_concept_id=38003564  # Not Hispanic
)

# Record cancer diagnosis
diagnosis = CancerDiagnosis.objects.create(
    person=patient,
    cancer_diagnosis_date='2023-01-15',
    primary_site_concept_id=4112853,  # Lung
    histology_concept_id=4115367     # Adenocarcinoma
)

# Record genomic variant
variant = GenomicVariant.objects.create(
    person=patient,
    variant_date='2023-02-01',
    chromosome='7',
    position_start=140753336,
    reference_allele='T',
    alternate_allele='A'
)
```

## Contributing

This project follows OMOP CDM standards and cancer research best practices. When adding new fields or tables, ensure alignment with:

- OMOP CDM specifications
- Cancer registry standards (NAACCR, SEER)
- Genomic data standards (GA4GH, HL7 FHIR)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

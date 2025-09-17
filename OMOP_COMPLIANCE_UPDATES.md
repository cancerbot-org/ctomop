# OMOP CDM Compliance Updates

## Changes Made

### 1. Removed VitalSignMeasurement Model
- **Rationale**: The custom VitalSignMeasurement model was non-standard and violated OMOP CDM principles
- **OMOP Standard**: Vital signs should be stored in the standard Measurement table using LOINC concepts
- **Benefits**: Enables interoperability with OMOP analytical tools and other OMOP implementations

### 2. Updated Models (omop_core/models.py)
- Removed VitalSignMeasurement class
- Added comments explaining proper OMOP approach for vital signs
- Included standard LOINC codes for reference

### 3. Updated Management Commands
- **populate_patient_info.py**: Modified get_vitals_data() to query Measurement table using LOINC concepts
- **create_enhanced_sample_data.py**: Updated to create standard Measurement records instead of VitalSignMeasurement
- **Created migrate_vitals_to_measurement.py**: Helper command for OMOP-compliant vital signs setup

### 4. Database Migration
- Created migration 0008_remove_vitalsignmeasurement.py to remove the table
- Migration includes documentation explaining the change

### 5. Documentation Updates
- Updated README.md to remove VitalSignMeasurement references
- Added section on OMOP-compliant vital signs storage
- Updated POPULATION_COMMAND_DOCUMENTATION.md
- Added LOINC concept mappings for reference

## Standard OMOP Vital Signs Approach

### LOINC Concepts Used
| Vital Sign | LOINC Code | Concept ID | Concept Name |
|------------|------------|------------|--------------|
| Systolic BP | 8480-6 | 3004249 | Systolic blood pressure |
| Diastolic BP | 8462-4 | 3012888 | Diastolic blood pressure |
| Heart Rate | 8867-4 | 3027018 | Heart rate |
| Weight | 29463-7 | 3025315 | Body weight |
| Height | 8302-2 | 3036277 | Body height |
| BMI | 39156-5 | 3038553 | Body mass index |
| Temperature | 8310-5 | 3020891 | Body temperature |
| O2 Saturation | 2708-6 | 3016502 | Oxygen saturation |

### Blood Pressure Storage
Following OMOP CDM best practices:
- Blood pressure is split into separate Measurement records
- One record for systolic value with LOINC 8480-6
- One record for diastolic value with LOINC 8462-4
- Both records share the same measurement_date/datetime

### Benefits of This Approach
1. **OMOP Compliance**: Follows official OMOP CDM standards
2. **Interoperability**: Works with standard OMOP tools and other implementations
3. **Standardization**: Uses internationally recognized LOINC terminology
4. **Analytics**: Enables cross-network studies and standardized analytics
5. **Future-Proof**: Aligns with OMOP community best practices

## Migration Guide

For existing implementations using VitalSignMeasurement:

1. **Run Migration**: `python manage.py migrate omop_core` (removes table)
2. **Setup Concepts**: `python manage.py migrate_vitals_to_measurement` (creates LOINC concepts)
3. **Migrate Data**: Use the migration template to convert existing vital signs data
4. **Update Queries**: Modify any code that queried VitalSignMeasurement to use Measurement table
5. **Test**: Verify vital signs data appears correctly in PatientInfo population

## Example OMOP-Compliant Vital Signs Query

```python
from omop_core.models import Measurement, Concept

# Get systolic blood pressure for a person
systolic_concept = Concept.objects.get(concept_code='8480-6', vocabulary_id='LOINC')
systolic_bp = Measurement.objects.filter(
    person_id=person_id,
    measurement_concept=systolic_concept
).order_by('-measurement_date').first()

if systolic_bp:
    value = systolic_bp.value_as_number
    date = systolic_bp.measurement_date
```

This approach ensures full OMOP CDM compliance while maintaining all functionality for clinical trial matching and patient profiling.

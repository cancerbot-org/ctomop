# PatientInfo Population Management Command

## Overview

This document describes the comprehensive `populate_patient_info` management command that was created to populate PatientInfo records from OMOP CDM and extension models. This command enables the transformation of normalized clinical data into comprehensive patient profiles suitable for clinical trial matching.

## What Was Built

### 1. Enhanced OMOP Data Model

The project was extended with comprehensive tables to support all PatientInfo fields:

#### Core OMOP Enhancements (omop_core/models.py)
- **Location**: Geographic location tracking with address, city, state, country
- **Person**: Enhanced with language support and death tracking for age calculation
- **ConditionOccurrence**: Extended with cancer staging (TNM, histology, grade, primary site)
- **MeasurementExtension**: Laboratory result interpretation and quality indicators
- **ObservationExtension**: Performance status assessment details
- **VitalSignMeasurement**: Specialized vital signs tracking (BP, weight, height, BMI)

#### Genomics Extensions (omop_genomics/models.py)
- **BiomarkerMeasurement**: Hormone receptors, HER2, PD-L1 testing
- **TumorAssessment**: RECIST evaluations and response tracking

#### Oncology Extensions (omop_oncology/models.py)
- **TreatmentLine**: Treatment line tracking with regimens and outcomes
- **SocialDeterminant**: Employment, insurance, housing status
- **HealthBehavior**: Smoking, alcohol, substance use history
- **InfectionStatus**: HIV, Hepatitis B/C, other infections

### 2. Population Management Command

#### Command Features
```bash
python manage.py populate_patient_info [options]

Options:
  --person-id ID     Process specific person only
  --force-update     Update existing PatientInfo records
  --verbose          Show detailed processing information
```

#### Data Extraction Functions

The command includes specialized functions to extract data from each model:

1. **get_demographics()**: Age calculation, gender mapping, race/ethnicity, language
2. **get_location_data()**: Geographic information from Location model
3. **get_disease_data()**: Cancer diagnosis, staging, histology from ConditionOccurrence
4. **get_treatment_data()**: Treatment lines, regimens, responses from TreatmentLine
5. **get_vitals_data()**: Blood pressure, weight, height from VitalSignMeasurement
6. **get_biomarker_data()**: PD-L1, hormone receptors from BiomarkerMeasurement
7. **get_social_data()**: Employment, insurance from SocialDeterminant
8. **get_behavior_data()**: Smoking status from HealthBehavior
9. **get_infection_data()**: HIV, Hepatitis status from InfectionStatus
10. **get_assessment_data()**: Tumor response from TumorAssessment
11. **get_laboratory_data()**: Lab values from Measurement
12. **get_performance_data()**: ECOG, Karnofsky from Observation

### 3. Comprehensive Field Mapping

The command maps data from OMOP models to PatientInfo fields:

#### Demographics
- Age calculated from birth year and death date
- Gender mapped from concept names
- Race/ethnicity from Person model
- Language preferences and skill levels

#### Disease Information
- Primary cancer diagnosis
- TNM staging (clinical and pathologic)
- Overall stage groups
- Histology and grade
- Primary site and metastatic status

#### Treatment History
- Treatment line numbers and regimens
- Treatment intent and setting
- Response outcomes
- Platinum, immunotherapy, chemotherapy flags

#### Biomarkers
- PD-L1 expression and assay method
- Hormone receptor status (ER/PR)
- HER2 status
- Triple negative breast cancer determination

#### Clinical Measurements
- Vital signs (blood pressure, heart rate)
- Anthropometric data (weight, height, BMI)
- Laboratory values (hemoglobin, platelets, creatinine, etc.)
- Performance status (ECOG, Karnofsky)

#### Social and Behavioral
- Employment and insurance status
- Smoking and substance use history
- Infection status (HIV, Hepatitis)
- Geographic risk factors

## Usage Examples

### Basic Usage
```bash
# Populate all patients
python manage.py populate_patient_info

# Process specific patient with verbose output
python manage.py populate_patient_info --person-id 1001 --verbose

# Force update existing records
python manage.py populate_patient_info --force-update
```

### Integration with Other Commands
```bash
# Create sample data, then populate PatientInfo
python manage.py create_enhanced_sample_data
python manage.py populate_patient_info --force-update

# Query results
python manage.py query_patient_info
```

## Example Output

The command produces comprehensive PatientInfo records like:

```
Example populated record (Person 1001):
  Age: 63
  Gender: F
  Disease: Lung Cancer
  Stage: II
  Location: Illinois, United States
  Language: en
  Weight: 52.0 kg
  Height: 173.0 cm
  BMI: 17.37
  ECOG: 0
  Karnofsky: 80
  First Line Therapy: VRd
  First Line Date: 2025-08-09
  First Line Outcome: Partial Response
  Biomarkers:
    ER Status: Unknown
    PR Status: Unknown
```

## Clinical Trial Matching Benefits

The populated PatientInfo records contain comprehensive data for:

✓ **Demographics**: Age, gender, race, ethnicity, language preferences
✓ **Geographic**: Location data for site-specific trials
✓ **Disease**: Detailed cancer staging and histology
✓ **Treatment**: Complete therapy history and responses
✓ **Biomarkers**: Molecular markers for targeted therapy eligibility
✓ **Performance**: Functional status assessments
✓ **Laboratory**: Organ function and safety parameters
✓ **Social**: Insurance and support system factors
✓ **Behavioral**: Risk factor assessment
✓ **Medical**: Comorbidities and infection status

## Technical Architecture

The command follows Django best practices:
- Atomic transactions for data integrity
- Proper error handling and logging
- Modular design with specialized extraction functions
- Flexible options for different use cases
- Timezone-aware datetime handling

## Database Migrations

All new models were properly migrated:
```bash
python manage.py makemigrations
python manage.py migrate
```

The command successfully applied:
- omop_core.0003: Location, Person enhancements, vital signs, measurement extensions
- omop_genomics.0002: Biomarker measurements and tumor assessments
- omop_oncology.0002: Treatment lines, social determinants, health behaviors, infection status

## Future Enhancements

The foundation is now in place for:
1. Real-time PatientInfo updates when source data changes
2. Automated trial matching based on populated criteria
3. Export to clinical trial matching systems
4. Integration with EHR systems for data ingestion
5. Advanced analytics on patient populations

## Conclusion

The `populate_patient_info` management command successfully bridges the gap between normalized OMOP CDM data and the comprehensive PatientInfo model needed for clinical trial matching. It demonstrates how Django management commands can elegantly handle complex data transformations while maintaining data integrity and providing flexible operation modes.

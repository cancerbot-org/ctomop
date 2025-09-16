# ctomop

Django project with comprehensive OMOP CDM models enhanced with oncology and genomic extensions for cancer clinical trial matching.

## Model Extensions & Field Additions

### OMOP Core Extensions (omop_core/models.py)

#### Enhanced Person Model
**Added Fields:**
- Language skills now handled via separate `PersonLanguageSkill` model for multiple languages with different skill levels

#### PersonLanguageSkill Model (NEW)
**Supports multiple languages per person with individual skill levels:**
- `language_concept` - Reference to language concept (English, Spanish, etc.)
- `skill_level` - Skill level choices: "speak", "write", "both"
- `is_primary` - Boolean flag for primary language
- Unique constraint per person/language combination
- Example: Person can have "English: both, Spanish: speak, French: write"

#### Enhanced ConditionOccurrence Model  
**OMOP-Compliant Approach:**
- Cancer staging information is stored in the **Observation table** following OMOP CDM best practices
- Primary site, histology, TNM staging, and grade are recorded as separate Observation records
- Uses standardized vocabularies (ICD-O-3, SNOMED-CT) for cancer concepts
- Observations are linked to ConditionOccurrence records using `observation_event_id` field (CDM v6.0 feature)

#### New VitalSignMeasurement Model
**Specialized vital signs tracking with fields:**
- `vital_sign_type` - Type of measurement (BLOOD_PRESSURE, WEIGHT, HEIGHT, etc.)
- `systolic_bp/diastolic_bp` - Blood pressure values
- `heart_rate` - Heart rate in BPM
- `weight/height` - Anthropometric measurements with units
- `bmi/bsa` - Calculated body metrics
- `measurement_position` - Patient position during measurement

#### New MeasurementExtension Model
**Laboratory result enhancements:**
- `normal_range_low/high` - Reference ranges
- `critical_low/high` - Critical value thresholds
- `clinical_significance` - Clinical interpretation
- `assay_method` - Laboratory methodology
- `test_quality` - Quality indicators (VALID, HEMOLYZED, etc.)

#### New ObservationExtension Model
**Clinical observation details:**
- `assessment_method` - How observation was made
- `assessor_type` - Who made the assessment (PHYSICIAN, NURSE, PATIENT)
- `symptom_severity` - Symptom severity scale
- `assessment_context` - Clinical context (BASELINE, PRE_TREATMENT, etc.)

### OMOP Genomics Extensions (omop_genomics/models.py)

#### New BiomarkerMeasurement Model
**Comprehensive biomarker testing:**
- `biomarker_type` - Type (HORMONE_RECEPTOR, HER2, PD_L1, GENETIC)
- `value_as_number/string` - Test results in multiple formats
- `assay_method` - Testing methodology (IHC, FISH, NGS)
- `clinical_significance` - Result interpretation (POSITIVE, NEGATIVE, EQUIVOCAL)
- `laboratory` - Testing facility
- `specimen_type` - Sample type (TISSUE, BLOOD, etc.)

#### New TumorAssessment Model
**Tumor response evaluation:**
- `assessment_method` - Imaging modality (CT_SCAN, MRI, PET_CT)
- `overall_response` - RECIST response (CR, PR, SD, PD)
- `target_lesion_sum` - Sum of target lesion measurements
- `new_lesions` - Presence of new lesions
- `progression_status` - Disease progression state
- `assessment_notes` - Clinical notes

### OMOP Oncology Extensions (omop_oncology/models.py)

#### New TreatmentLine Model
**Treatment line tracking:**
- `line_number` - Treatment line sequence (1, 2, 3, etc.)
- `treatment_intent` - Intent (CURATIVE, PALLIATIVE, ADJUVANT)
- `regimen_name` - Treatment regimen name
- `treatment_setting` - Setting (INPATIENT, OUTPATIENT, CLINICAL_TRIAL)
- Treatment type flags: `is_platinum_based`, `is_immunotherapy`, `is_targeted_therapy`
- `best_response` - Best response achieved (CR, PR, SD, PD)
- `treatment_outcome` - Reason for discontinuation
- `ecog_at_start/karnofsky_at_start` - Performance status at treatment start

#### New SocialDeterminant Model
**Social determinants of health:**
- `determinant_category` - Category (HOUSING, EMPLOYMENT, INSURANCE, etc.)
- `value_as_string/boolean` - Determinant values
- `risk_level` - Associated risk level (HIGH, MODERATE, LOW)
- `assessment_details` - Additional context

#### New HealthBehavior Model
**Health behavior tracking:**
- `behavior_type` - Type (TOBACCO_USE, ALCOHOL_USE, SUBSTANCE_USE)
- `current_status` - Status (CURRENT, FORMER, NEVER)
- `frequency/amount_per_day` - Usage patterns
- `duration_years` - Duration of behavior
- `quit_date` - Cessation date for former users
- `cessation_attempts` - Number of quit attempts

#### New InfectionStatus Model
**Infection status tracking:**
- `infection_type` - Type (HIV, HEPATITIS_B, HEPATITIS_C, TB)
- `infection_status` - Status (POSITIVE, NEGATIVE, INDETERMINATE)
- `test_method` - Testing methodology
- `viral_load` - Quantitative viral measurements
- `is_active_infection` - Current infection status

### PatientInfo Model (Comprehensive Clinical Profile)
**Integration model with 100+ fields covering:**
- Demographics and anthropometrics
- Disease staging and histology
- Treatment history across all lines
- Biomarker results (ER, PR, HER2, PD-L1, genetic mutations)
- Laboratory values with units
- Performance status assessments
- Social determinants and risk factors
- Geographic and language information

## Management Commands

### populate_patient_info
Comprehensive command to extract data from all OMOP models and populate PatientInfo records:
```bash
python manage.py populate_patient_info --force-update --verbose
```

### manage_language_skills
Command to manage multiple language skills for persons:
```bash
# Create sample language concepts
python manage.py manage_language_skills --create-sample-concepts

# Add language skills
python manage.py manage_language_skills --person-id 1001 --add-language "English:both"
python manage.py manage_language_skills --person-id 1001 --add-language "Spanish:speak"

# Set primary language
python manage.py manage_language_skills --person-id 1001 --set-primary "English"

# List all languages for a person
python manage.py manage_language_skills --person-id 1001 --list-languages
```

### create_cancer_staging_observations
OMOP-compliant command to create cancer staging as Observation records:
```bash
# Create cancer staging concepts
python manage.py create_cancer_staging_observations --create-concepts

# Create staging observations for a condition
python manage.py create_cancer_staging_observations --person-id 1001 --condition-occurrence-id 5001
```

### Enhanced Data Pipeline
The extensions enable a complete data pipeline from raw OMOP data to clinical trial-ready patient profiles through intelligent field mapping and data consolidation.

## OMOP CDM Compliance

### Cancer Staging Approach
This project follows OMOP CDM best practices by storing cancer staging information in the **Observation table** rather than extending core clinical event tables. This approach:

- **Maintains OMOP Standards**: Uses existing OMOP tables as designed
- **Supports Standard Vocabularies**: Leverages ICD-O-3, SNOMED-CT, and other standardized terminologies
- **Enables Flexible Staging**: Supports any staging system (AJCC, TNM, etc.) through standardized concepts
- **Links Related Data**: Uses CDM v6.0 `observation_event_id` to link staging observations to conditions

### Cancer Data Storage Pattern:
- **Primary Site**: Observation with ICD-O-3 topography concept
- **Histology**: Observation with ICD-O-3 morphology concept  
- **TNM Staging**: Separate observations for T, N, M categories
- **Stage Group**: Observation with overall stage concept
- **Grade**: Observation with tumor grade concept

This approach ensures compatibility with OMOP analytic tools and enables standardized cross-network studies.

## Recent Updates

### PatientInfo Model Added
A comprehensive PatientInfo model has been integrated from the [exactomop repository](https://github.com/cancerbot-org/exactomop), providing a research-friendly, denormalized view of patient data optimized for clinical trial eligibility screening.

**Key Features:**
- Complete patient demographics and disease information
- Treatment history tracking (1st, 2nd, later lines)
- Laboratory values with proper units
- Cancer-specific biomarkers (ER, PR, HER2, genetic mutations)
- Risk factors and behavioral data
- Automatic BMI calculation
- Integration with OMOP CDM Person model

**Documentation:** See [PATIENTINFO_README.md](PATIENTINFO_README.md) for detailed usage information.

## Quick Start with PatientInfo

```bash
# Create sample data
python manage.py populate_patient_info --count 5

# Query patient information
python manage.py query_patient_info

# Query specific patient
python manage.py query_patient_info --person-id 1001

# Filter by disease
python manage.py query_patient_info --disease "breast"
```

## Project Structure

The project consists of three main Django apps:

- **omop_core**: Core OMOP CDM models and PatientInfo model
- **omop_genomics**: Genomic extensions for OMOP
- **omop_oncology**: Oncology-specific extensions for OMOP

from django.contrib import admin
from .models import (
    Vocabulary, Domain, ConceptClass, Concept, Person, 
    VisitOccurrence, ConditionOccurrence, DrugExposure, 
    Measurement, Observation, PatientInfo
)


@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display = ('vocabulary_id', 'vocabulary_name', 'vocabulary_version')
    search_fields = ('vocabulary_id', 'vocabulary_name')


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain_id', 'domain_name')
    search_fields = ('domain_id', 'domain_name')


@admin.register(ConceptClass)
class ConceptClassAdmin(admin.ModelAdmin):
    list_display = ('concept_class_id', 'concept_class_name')
    search_fields = ('concept_class_id', 'concept_class_name')


@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = ('concept_id', 'concept_name', 'domain', 'vocabulary', 'concept_class', 'standard_concept')
    list_filter = ('domain', 'vocabulary', 'concept_class', 'standard_concept')
    search_fields = ('concept_id', 'concept_name', 'concept_code')
    readonly_fields = ('concept_id',)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('person_id', 'year_of_birth', 'gender_concept', 'race_concept', 'ethnicity_concept')
    list_filter = ('gender_concept', 'race_concept', 'ethnicity_concept')
    search_fields = ('person_id', 'person_source_value')


@admin.register(VisitOccurrence)
class VisitOccurrenceAdmin(admin.ModelAdmin):
    list_display = ('visit_occurrence_id', 'person', 'visit_concept', 'visit_start_date', 'visit_end_date')
    list_filter = ('visit_concept', 'visit_type_concept')
    search_fields = ('visit_occurrence_id', 'person__person_id')
    date_hierarchy = 'visit_start_date'


@admin.register(ConditionOccurrence)
class ConditionOccurrenceAdmin(admin.ModelAdmin):
    list_display = ('condition_occurrence_id', 'person', 'condition_concept', 'condition_start_date')
    list_filter = ('condition_concept', 'condition_type_concept')
    search_fields = ('condition_occurrence_id', 'person__person_id')
    date_hierarchy = 'condition_start_date'


@admin.register(DrugExposure)
class DrugExposureAdmin(admin.ModelAdmin):
    list_display = ('drug_exposure_id', 'person', 'drug_concept', 'drug_exposure_start_date')
    list_filter = ('drug_concept', 'drug_type_concept')
    search_fields = ('drug_exposure_id', 'person__person_id')
    date_hierarchy = 'drug_exposure_start_date'


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('measurement_id', 'person', 'measurement_concept', 'measurement_date', 'value_as_number')
    list_filter = ('measurement_concept', 'measurement_type_concept')
    search_fields = ('measurement_id', 'person__person_id')
    date_hierarchy = 'measurement_date'


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ('observation_id', 'person', 'observation_concept', 'observation_date')
    list_filter = ('observation_concept', 'observation_type_concept')
    search_fields = ('observation_id', 'person__person_id')
    date_hierarchy = 'observation_date'


@admin.register(PatientInfo)
class PatientInfoAdmin(admin.ModelAdmin):
    list_display = ('person', 'patient_age', 'gender', 'disease', 'stage', 'therapy_lines_count')
    list_filter = ('gender', 'disease', 'stage', 'no_other_active_malignancies')
    search_fields = ('person__person_id', 'disease', 'condition_code_icd_10')
    readonly_fields = ('bmi',)
    
    fieldsets = (
        ('Patient Link', {
            'fields': ('person',)
        }),
        ('Demographics', {
            'fields': ('patient_age', 'gender', 'weight', 'weight_units', 'height', 'height_units', 'bmi', 'ethnicity')
        }),
        ('Disease Information', {
            'fields': ('disease', 'stage', 'karnofsky_performance_score', 'ecog_performance_status', 
                      'no_other_active_malignancies', 'peripheral_neuropathy_grade')
        }),
        ('Treatment History', {
            'fields': ('prior_therapy', 'first_line_therapy', 'first_line_date', 'first_line_outcome',
                      'second_line_therapy', 'second_line_date', 'second_line_outcome',
                      'therapy_lines_count', 'last_treatment')
        }),
        ('Laboratory Values', {
            'fields': ('hemoglobin_level', 'hemoglobin_level_units', 'platelet_count', 'platelet_count_units',
                      'white_blood_cell_count', 'white_blood_cell_count_units', 'serum_creatinine_level',
                      'serum_creatinine_level_units', 'liver_enzyme_levels_ast', 'liver_enzyme_levels_alt')
        }),
        ('Cancer-Specific', {
            'fields': ('estrogen_receptor_status', 'progesterone_receptor_status', 'her2_status',
                      'genetic_mutations', 'pd_l1_tumor_cels', 'ki67_proliferation_index')
        }),
        ('Risk Factors & Behavior', {
            'fields': ('consent_capability', 'caregiver_availability_status', 'no_tobacco_use_status',
                      'tobacco_use_details', 'no_substance_use_status', 'substance_use_details')
        }),
        ('Geographic Information', {
            'fields': ('country', 'region', 'postal_code', 'languages', 'language_skill_level')
        })
    )

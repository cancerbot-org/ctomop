from django.contrib import admin
from .models import (
    Vocabulary, Domain, ConceptClass, Concept, Person, 
    VisitOccurrence, ConditionOccurrence, DrugExposure, 
    Measurement, Observation
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

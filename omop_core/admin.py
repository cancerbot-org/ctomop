from django.contrib import admin
from .models import (
    Vocabulary, Domain, ConceptClass, Concept, ConceptRelationship,
    ConceptSynonym, ConceptAncestor, SourceToConceptMap, DrugStrength,
    CdmSource, Metadata, Location, CareSite, Provider, Person,
    ObservationPeriod, VisitOccurrence, VisitDetail
)
from .clinical_models import (
    ConditionOccurrence, DrugExposure, ProcedureOccurrence, DeviceExposure,
    Measurement, Observation, Death, Note, NoteNlp, Specimen, FactRelationship
)
from .health_system_models import (
    PayerPlanPeriod, Cost, DoseEra, DrugEra, ConditionEra, Cohort, CohortAttribute
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
    list_display = ('concept_id', 'concept_name', 'domain', 'vocabulary', 'standard_concept')
    list_filter = ('domain', 'vocabulary', 'standard_concept')
    search_fields = ('concept_id', 'concept_name', 'concept_code')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('person_id', 'year_of_birth', 'gender_concept', 'race_concept')
    list_filter = ('year_of_birth', 'gender_concept')
    search_fields = ('person_id', 'person_source_value')


@admin.register(VisitOccurrence)
class VisitOccurrenceAdmin(admin.ModelAdmin):
    list_display = ('visit_occurrence_id', 'person', 'visit_concept', 'visit_start_date', 'visit_end_date')
    list_filter = ('visit_concept', 'visit_start_date')
    search_fields = ('person__person_id',)


@admin.register(ConditionOccurrence)
class ConditionOccurrenceAdmin(admin.ModelAdmin):
    list_display = ('condition_occurrence_id', 'person', 'condition_concept', 'condition_start_date')
    list_filter = ('condition_concept', 'condition_start_date')
    search_fields = ('person__person_id',)


@admin.register(DrugExposure)
class DrugExposureAdmin(admin.ModelAdmin):
    list_display = ('drug_exposure_id', 'person', 'drug_concept', 'drug_exposure_start_date')
    list_filter = ('drug_concept', 'drug_exposure_start_date')
    search_fields = ('person__person_id',)


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('measurement_id', 'person', 'measurement_concept', 'measurement_date', 'value_as_number')
    list_filter = ('measurement_concept', 'measurement_date')
    search_fields = ('person__person_id',)


# Register other models with basic admin
admin.site.register(ConceptRelationship)
admin.site.register(ConceptSynonym)
admin.site.register(ConceptAncestor)
admin.site.register(SourceToConceptMap)
admin.site.register(DrugStrength)
admin.site.register(CdmSource)
admin.site.register(Metadata)
admin.site.register(Location)
admin.site.register(CareSite)
admin.site.register(Provider)
admin.site.register(ObservationPeriod)
admin.site.register(VisitDetail)
admin.site.register(ProcedureOccurrence)
admin.site.register(DeviceExposure)
admin.site.register(Observation)
admin.site.register(Death)
admin.site.register(Note)
admin.site.register(NoteNlp)
admin.site.register(Specimen)
admin.site.register(FactRelationship)
admin.site.register(PayerPlanPeriod)
admin.site.register(Cost)
admin.site.register(DoseEra)
admin.site.register(DrugEra)
admin.site.register(ConditionEra)
admin.site.register(Cohort)
admin.site.register(CohortAttribute)

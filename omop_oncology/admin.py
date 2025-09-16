from django.contrib import admin
from .models import (
    Episode, EpisodeEvent, CancerDiagnosis, CancerTreatment,
    CancerSurgery, CancerRadiation, CancerBiomarker, CancerResponse,
    CancerMetastasis
)


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('episode_id', 'person', 'episode_concept', 'episode_start_date', 'episode_end_date')
    list_filter = ('episode_concept', 'episode_start_date')
    search_fields = ('person__person_id',)


@admin.register(CancerDiagnosis)
class CancerDiagnosisAdmin(admin.ModelAdmin):
    list_display = ('cancer_diagnosis_id', 'person', 'cancer_diagnosis_date', 'primary_site_concept', 'histology_concept')
    list_filter = ('primary_site_concept', 'histology_concept', 'cancer_diagnosis_date')
    search_fields = ('person__person_id',)


@admin.register(CancerTreatment)
class CancerTreatmentAdmin(admin.ModelAdmin):
    list_display = ('cancer_treatment_id', 'person', 'treatment_concept', 'treatment_start_date', 'line_of_therapy')
    list_filter = ('treatment_concept', 'treatment_type_concept', 'treatment_start_date')
    search_fields = ('person__person_id',)


@admin.register(CancerSurgery)
class CancerSurgeryAdmin(admin.ModelAdmin):
    list_display = ('cancer_surgery_id', 'person', 'surgery_concept', 'surgery_date', 'surgical_margin_concept')
    list_filter = ('surgery_concept', 'surgery_date')
    search_fields = ('person__person_id',)


@admin.register(CancerRadiation)
class CancerRadiationAdmin(admin.ModelAdmin):
    list_display = ('cancer_radiation_id', 'person', 'radiation_concept', 'radiation_start_date', 'total_dose_gy')
    list_filter = ('radiation_concept', 'radiation_start_date')
    search_fields = ('person__person_id',)


@admin.register(CancerBiomarker)
class CancerBiomarkerAdmin(admin.ModelAdmin):
    list_display = ('cancer_biomarker_id', 'person', 'biomarker_concept', 'biomarker_date', 'biomarker_result_concept')
    list_filter = ('biomarker_concept', 'biomarker_type_concept', 'biomarker_date')
    search_fields = ('person__person_id',)


@admin.register(CancerResponse)
class CancerResponseAdmin(admin.ModelAdmin):
    list_display = ('cancer_response_id', 'person', 'response_concept', 'response_date')
    list_filter = ('response_concept', 'response_date')
    search_fields = ('person__person_id',)


@admin.register(CancerMetastasis)
class CancerMetastasisAdmin(admin.ModelAdmin):
    list_display = ('cancer_metastasis_id', 'person', 'metastasis_site_concept', 'metastasis_date')
    list_filter = ('metastasis_site_concept', 'metastasis_date')
    search_fields = ('person__person_id',)


admin.site.register(EpisodeEvent)

from django.contrib import admin
from .models import Episode, EpisodeEvent, CancerModifier, StemTable, Histology


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('episode_id', 'person', 'episode_concept', 'episode_start_date', 'episode_end_date')
    list_filter = ('episode_concept', 'episode_type_concept')
    search_fields = ('episode_id', 'person__person_id')
    date_hierarchy = 'episode_start_date'


@admin.register(EpisodeEvent)
class EpisodeEventAdmin(admin.ModelAdmin):
    list_display = ('episode_id', 'event_id', 'episode_event_field_concept')
    search_fields = ('episode_id', 'event_id')


@admin.register(CancerModifier)
class CancerModifierAdmin(admin.ModelAdmin):
    list_display = ('cancer_modifier_id', 'person', 'cancer_modifier_concept')
    list_filter = ('cancer_modifier_concept',)
    search_fields = ('cancer_modifier_id', 'person__person_id')


@admin.register(StemTable)
class StemTableAdmin(admin.ModelAdmin):
    list_display = ('id', 'person', 'domain_id', 'concept', 'start_date')
    list_filter = ('domain_id', 'concept')
    search_fields = ('id', 'person__person_id')
    date_hierarchy = 'start_date'


@admin.register(Histology)
class HistologyAdmin(admin.ModelAdmin):
    list_display = ('histology_id', 'person', 'concept', 'histology_date')
    list_filter = ('concept', 'histology_type_concept')
    search_fields = ('histology_id', 'person__person_id')
    date_hierarchy = 'histology_date'

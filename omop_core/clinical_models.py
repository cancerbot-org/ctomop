from django.db import models
from .models import Concept, Person, VisitOccurrence, VisitDetail, Provider, CareSite


class ConditionOccurrence(models.Model):
    """
    CONDITION_OCCURRENCE table contains records of Events of a Person suggesting the presence of a disease or medical condition stated as a diagnosis, a sign, or a symptom.
    """
    condition_occurrence_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    condition_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='condition_concept_id')
    condition_start_date = models.DateField()
    condition_start_datetime = models.DateTimeField(null=True, blank=True)
    condition_end_date = models.DateField(null=True, blank=True)
    condition_end_datetime = models.DateTimeField(null=True, blank=True)
    condition_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='condition_types', db_column='condition_type_concept_id')
    condition_status_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='condition_statuses', db_column='condition_status_concept_id', null=True, blank=True)
    stop_reason = models.CharField(max_length=20, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    condition_source_value = models.CharField(max_length=50, null=True, blank=True)
    condition_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='condition_sources', db_column='condition_source_concept_id', null=True, blank=True)
    condition_status_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'condition_occurrence'

    def __str__(self):
        return f"Condition {self.condition_occurrence_id} for {self.person}"


class DrugExposure(models.Model):
    """
    DRUG_EXPOSURE table captures records about the utilization of a Drug when ingested or otherwise introduced into the body.
    """
    drug_exposure_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    drug_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='drug_concept_id')
    drug_exposure_start_date = models.DateField()
    drug_exposure_start_datetime = models.DateTimeField(null=True, blank=True)
    drug_exposure_end_date = models.DateField()
    drug_exposure_end_datetime = models.DateTimeField(null=True, blank=True)
    verbatim_end_date = models.DateField(null=True, blank=True)
    drug_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='drug_types', db_column='drug_type_concept_id')
    stop_reason = models.CharField(max_length=20, null=True, blank=True)
    refills = models.IntegerField(null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    days_supply = models.IntegerField(null=True, blank=True)
    sig = models.TextField(null=True, blank=True)
    route_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='drug_routes', db_column='route_concept_id', null=True, blank=True)
    lot_number = models.CharField(max_length=50, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    drug_source_value = models.CharField(max_length=50, null=True, blank=True)
    drug_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='drug_sources', db_column='drug_source_concept_id', null=True, blank=True)
    route_source_value = models.CharField(max_length=50, null=True, blank=True)
    dose_unit_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'drug_exposure'

    def __str__(self):
        return f"Drug Exposure {self.drug_exposure_id} for {self.person}"


class ProcedureOccurrence(models.Model):
    """
    PROCEDURE_OCCURRENCE table contains records of activities or processes ordered by, or carried out by, a healthcare provider on the patient to have a diagnostic or therapeutic purpose.
    """
    procedure_occurrence_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    procedure_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='procedure_concept_id')
    procedure_date = models.DateField()
    procedure_datetime = models.DateTimeField(null=True, blank=True)
    procedure_end_date = models.DateField(null=True, blank=True)
    procedure_end_datetime = models.DateTimeField(null=True, blank=True)
    procedure_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='procedure_types', db_column='procedure_type_concept_id')
    modifier_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='procedure_modifiers', db_column='modifier_concept_id', null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    procedure_source_value = models.CharField(max_length=50, null=True, blank=True)
    procedure_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='procedure_sources', db_column='procedure_source_concept_id', null=True, blank=True)
    modifier_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'procedure_occurrence'

    def __str__(self):
        return f"Procedure {self.procedure_occurrence_id} for {self.person}"


class DeviceExposure(models.Model):
    """
    DEVICE_EXPOSURE table captures information about a person's exposure to a foreign physical object or instrument which is used for diagnostic or therapeutic purposes.
    """
    device_exposure_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    device_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='device_concept_id')
    device_exposure_start_date = models.DateField()
    device_exposure_start_datetime = models.DateTimeField(null=True, blank=True)
    device_exposure_end_date = models.DateField(null=True, blank=True)
    device_exposure_end_datetime = models.DateTimeField(null=True, blank=True)
    device_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='device_types', db_column='device_type_concept_id')
    unique_device_id = models.CharField(max_length=255, null=True, blank=True)
    production_id = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    device_source_value = models.CharField(max_length=50, null=True, blank=True)
    device_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='device_sources', db_column='device_source_concept_id', null=True, blank=True)
    unit_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='device_units', db_column='unit_concept_id', null=True, blank=True)
    unit_source_value = models.CharField(max_length=50, null=True, blank=True)
    unit_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='device_unit_sources', db_column='unit_source_concept_id', null=True, blank=True)

    class Meta:
        db_table = 'device_exposure'

    def __str__(self):
        return f"Device Exposure {self.device_exposure_id} for {self.person}"


class Measurement(models.Model):
    """
    MEASUREMENT table contains records of Measurements, i.e. structured values (numerical or categorical) obtained through systematic and standardized examination or testing of a Person or Person's sample.
    """
    measurement_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    measurement_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='measurement_concept_id')
    measurement_date = models.DateField()
    measurement_datetime = models.DateTimeField(null=True, blank=True)
    measurement_time = models.CharField(max_length=10, null=True, blank=True)
    measurement_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='measurement_types', db_column='measurement_type_concept_id')
    operator_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='measurement_operators', db_column='operator_concept_id', null=True, blank=True)
    value_as_number = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    value_as_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='measurement_values', db_column='value_as_concept_id', null=True, blank=True)
    unit_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='measurement_units', db_column='unit_concept_id', null=True, blank=True)
    range_low = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    range_high = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    measurement_source_value = models.CharField(max_length=50, null=True, blank=True)
    measurement_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='measurement_sources', db_column='measurement_source_concept_id', null=True, blank=True)
    unit_source_value = models.CharField(max_length=50, null=True, blank=True)
    unit_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='measurement_unit_sources', db_column='unit_source_concept_id', null=True, blank=True)
    value_source_value = models.CharField(max_length=50, null=True, blank=True)
    measurement_event_id = models.IntegerField(null=True, blank=True)
    meas_event_field_concept_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'measurement'

    def __str__(self):
        return f"Measurement {self.measurement_id} for {self.person}"


class Observation(models.Model):
    """
    OBSERVATION table captures clinical facts about a Person obtained in the context of examination, questioning, or a procedure.
    """
    observation_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    observation_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='observation_concept_id')
    observation_date = models.DateField()
    observation_datetime = models.DateTimeField(null=True, blank=True)
    observation_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='observation_types', db_column='observation_type_concept_id')
    value_as_number = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    value_as_string = models.CharField(max_length=60, null=True, blank=True)
    value_as_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='observation_values', db_column='value_as_concept_id', null=True, blank=True)
    qualifier_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='observation_qualifiers', db_column='qualifier_concept_id', null=True, blank=True)
    unit_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='observation_units', db_column='unit_concept_id', null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    observation_source_value = models.CharField(max_length=50, null=True, blank=True)
    observation_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='observation_sources', db_column='observation_source_concept_id', null=True, blank=True)
    unit_source_value = models.CharField(max_length=50, null=True, blank=True)
    qualifier_source_value = models.CharField(max_length=50, null=True, blank=True)
    value_source_value = models.CharField(max_length=50, null=True, blank=True)
    observation_event_id = models.IntegerField(null=True, blank=True)
    obs_event_field_concept_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'observation'

    def __str__(self):
        return f"Observation {self.observation_id} for {self.person}"


class Death(models.Model):
    """
    DEATH table contains the clinical event for how and when a Person dies.
    """
    person = models.OneToOneField(Person, on_delete=models.CASCADE, primary_key=True)
    death_date = models.DateField()
    death_datetime = models.DateTimeField(null=True, blank=True)
    death_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='death_type_concept_id')
    cause_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='death_causes', db_column='cause_concept_id', null=True, blank=True)
    cause_source_value = models.CharField(max_length=50, null=True, blank=True)
    cause_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='death_cause_sources', db_column='cause_source_concept_id', null=True, blank=True)

    class Meta:
        db_table = 'death'

    def __str__(self):
        return f"Death of {self.person}"


class Note(models.Model):
    """
    NOTE table captures unstructured information that was recorded by a provider about a patient in free text notes on a given date.
    """
    note_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    note_date = models.DateField()
    note_datetime = models.DateTimeField(null=True, blank=True)
    note_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='note_type_concept_id')
    note_class_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='note_classes', db_column='note_class_concept_id')
    note_title = models.CharField(max_length=250, null=True, blank=True)
    note_text = models.TextField()
    encoding_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='note_encodings', db_column='encoding_concept_id')
    language_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='note_languages', db_column='language_concept_id')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    note_source_value = models.CharField(max_length=50, null=True, blank=True)
    note_event_id = models.IntegerField(null=True, blank=True)
    note_event_field_concept_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'note'

    def __str__(self):
        return f"Note {self.note_id} for {self.person}"


class NoteNlp(models.Model):
    """
    NOTE_NLP table encodes all output of NLP on clinical notes.
    """
    note_nlp_id = models.AutoField(primary_key=True)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    section_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='note_nlp_sections', db_column='section_concept_id', null=True, blank=True)
    snippet = models.CharField(max_length=250, null=True, blank=True)
    offset = models.CharField(max_length=50, null=True, blank=True)
    lexical_variant = models.CharField(max_length=250)
    note_nlp_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='note_nlp_concept_id', null=True, blank=True)
    note_nlp_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='note_nlp_sources', db_column='note_nlp_source_concept_id', null=True, blank=True)
    nlp_system = models.CharField(max_length=250, null=True, blank=True)
    nlp_date = models.DateField()
    nlp_datetime = models.DateTimeField(null=True, blank=True)
    term_exists = models.CharField(max_length=1, null=True, blank=True)
    term_temporal = models.CharField(max_length=50, null=True, blank=True)
    term_modifiers = models.CharField(max_length=2000, null=True, blank=True)

    class Meta:
        db_table = 'note_nlp'

    def __str__(self):
        return f"Note NLP {self.note_nlp_id} for {self.note}"


class Specimen(models.Model):
    """
    SPECIMEN table contains the records identifying biological samples from a person.
    """
    specimen_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    specimen_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='specimen_concept_id')
    specimen_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='specimen_types', db_column='specimen_type_concept_id')
    specimen_date = models.DateField()
    specimen_datetime = models.DateTimeField(null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='specimen_units', db_column='unit_concept_id', null=True, blank=True)
    anatomic_site_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='specimen_anatomic_sites', db_column='anatomic_site_concept_id', null=True, blank=True)
    disease_status_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='specimen_disease_statuses', db_column='disease_status_concept_id', null=True, blank=True)
    specimen_source_id = models.CharField(max_length=50, null=True, blank=True)
    specimen_source_value = models.CharField(max_length=50, null=True, blank=True)
    unit_source_value = models.CharField(max_length=50, null=True, blank=True)
    anatomic_site_source_value = models.CharField(max_length=50, null=True, blank=True)
    disease_status_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'specimen'

    def __str__(self):
        return f"Specimen {self.specimen_id} for {self.person}"


class FactRelationship(models.Model):
    """
    FACT_RELATIONSHIP table contains records about the relationships between facts stored as records in any table of the CDM.
    """
    domain_concept_id_1 = models.IntegerField()
    fact_id_1 = models.IntegerField()
    domain_concept_id_2 = models.IntegerField()
    fact_id_2 = models.IntegerField()
    relationship_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='relationship_concept_id')

    class Meta:
        db_table = 'fact_relationship'
        unique_together = ('domain_concept_id_1', 'fact_id_1', 'domain_concept_id_2', 'fact_id_2', 'relationship_concept')

    def __str__(self):
        return f"Fact Relationship {self.fact_id_1} -> {self.fact_id_2}"
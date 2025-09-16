from django.db import models


class Vocabulary(models.Model):
    """OMOP CDM Vocabulary table - standardized vocabularies."""
    vocabulary_id = models.CharField(max_length=20, primary_key=True)
    vocabulary_name = models.CharField(max_length=255)
    vocabulary_reference = models.CharField(max_length=255, null=True, blank=True)
    vocabulary_version = models.CharField(max_length=255, null=True, blank=True)
    vocabulary_concept_id = models.IntegerField()

    class Meta:
        db_table = 'vocabulary'

    def __str__(self):
        return f"{self.vocabulary_id}: {self.vocabulary_name}"


class Domain(models.Model):
    """OMOP CDM Domain table - high-level classification of concepts."""
    domain_id = models.CharField(max_length=20, primary_key=True)
    domain_name = models.CharField(max_length=255)
    domain_concept_id = models.IntegerField()

    class Meta:
        db_table = 'domain'

    def __str__(self):
        return f"{self.domain_id}: {self.domain_name}"


class ConceptClass(models.Model):
    """OMOP CDM Concept Class table - classification of concepts within domains."""
    concept_class_id = models.CharField(max_length=20, primary_key=True)
    concept_class_name = models.CharField(max_length=255)
    concept_class_concept_id = models.IntegerField()

    class Meta:
        db_table = 'concept_class'

    def __str__(self):
        return f"{self.concept_class_id}: {self.concept_class_name}"


class Concept(models.Model):
    """OMOP CDM Concept table - standardized terminologies."""
    concept_id = models.IntegerField(primary_key=True)
    concept_name = models.CharField(max_length=255)
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT, db_column='domain_id')
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.PROTECT, db_column='vocabulary_id')
    concept_class = models.ForeignKey(ConceptClass, on_delete=models.PROTECT, db_column='concept_class_id')
    standard_concept = models.CharField(max_length=1, null=True, blank=True)
    concept_code = models.CharField(max_length=50)
    valid_start_date = models.DateField()
    valid_end_date = models.DateField()
    invalid_reason = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        db_table = 'concept'

    def __str__(self):
        return f"{self.concept_id}: {self.concept_name}"


class Person(models.Model):
    """OMOP CDM Person table - demographic information about individuals."""
    person_id = models.BigIntegerField(primary_key=True)
    gender_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='person_gender', db_column='gender_concept_id')
    year_of_birth = models.IntegerField()
    month_of_birth = models.IntegerField(null=True, blank=True)
    day_of_birth = models.IntegerField(null=True, blank=True)
    birth_datetime = models.DateTimeField(null=True, blank=True)
    race_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='person_race', db_column='race_concept_id')
    ethnicity_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='person_ethnicity', db_column='ethnicity_concept_id')
    location_id = models.IntegerField(null=True, blank=True)
    provider_id = models.IntegerField(null=True, blank=True)
    care_site_id = models.IntegerField(null=True, blank=True)
    person_source_value = models.CharField(max_length=50, null=True, blank=True)
    gender_source_value = models.CharField(max_length=50, null=True, blank=True)
    gender_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='person_gender_source', db_column='gender_source_concept_id', null=True, blank=True)
    race_source_value = models.CharField(max_length=50, null=True, blank=True)
    race_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='person_race_source', db_column='race_source_concept_id', null=True, blank=True)
    ethnicity_source_value = models.CharField(max_length=50, null=True, blank=True)
    ethnicity_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='person_ethnicity_source', db_column='ethnicity_source_concept_id', null=True, blank=True)

    class Meta:
        db_table = 'person'

    def __str__(self):
        return f"Person {self.person_id}"


class VisitOccurrence(models.Model):
    """OMOP CDM Visit Occurrence table - healthcare visits."""
    visit_occurrence_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    visit_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='visit_occurrences', db_column='visit_concept_id')
    visit_start_date = models.DateField()
    visit_start_datetime = models.DateTimeField(null=True, blank=True)
    visit_end_date = models.DateField()
    visit_end_datetime = models.DateTimeField(null=True, blank=True)
    visit_type_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='visit_type_occurrences', db_column='visit_type_concept_id')
    provider_id = models.IntegerField(null=True, blank=True)
    care_site_id = models.IntegerField(null=True, blank=True)
    visit_source_value = models.CharField(max_length=50, null=True, blank=True)
    visit_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='visit_source_occurrences', db_column='visit_source_concept_id', null=True, blank=True)
    admitted_from_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='visit_admitted_from', db_column='admitted_from_concept_id', null=True, blank=True)
    admitted_from_source_value = models.CharField(max_length=50, null=True, blank=True)
    discharged_to_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='visit_discharged_to', db_column='discharged_to_concept_id', null=True, blank=True)
    discharged_to_source_value = models.CharField(max_length=50, null=True, blank=True)
    preceding_visit_occurrence_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'visit_occurrence'

    def __str__(self):
        return f"Visit {self.visit_occurrence_id} for Person {self.person_id}"


class ConditionOccurrence(models.Model):
    """OMOP CDM Condition Occurrence table - diagnoses and conditions."""
    condition_occurrence_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    condition_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='condition_occurrences', db_column='condition_concept_id')
    condition_start_date = models.DateField()
    condition_start_datetime = models.DateTimeField(null=True, blank=True)
    condition_end_date = models.DateField(null=True, blank=True)
    condition_end_datetime = models.DateTimeField(null=True, blank=True)
    condition_type_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='condition_type_occurrences', db_column='condition_type_concept_id')
    condition_status_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='condition_status_occurrences', db_column='condition_status_concept_id', null=True, blank=True)
    stop_reason = models.CharField(max_length=20, null=True, blank=True)
    provider_id = models.IntegerField(null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.SET_NULL, db_column='visit_occurrence_id', null=True, blank=True)
    visit_detail_id = models.IntegerField(null=True, blank=True)
    condition_source_value = models.CharField(max_length=50, null=True, blank=True)
    condition_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='condition_source_occurrences', db_column='condition_source_concept_id', null=True, blank=True)
    condition_status_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'condition_occurrence'

    def __str__(self):
        return f"Condition {self.condition_occurrence_id} for Person {self.person_id}"


class DrugExposure(models.Model):
    """OMOP CDM Drug Exposure table - medications and treatments."""
    drug_exposure_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    drug_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='drug_exposures', db_column='drug_concept_id')
    drug_exposure_start_date = models.DateField()
    drug_exposure_start_datetime = models.DateTimeField(null=True, blank=True)
    drug_exposure_end_date = models.DateField()
    drug_exposure_end_datetime = models.DateTimeField(null=True, blank=True)
    verbatim_end_date = models.DateField(null=True, blank=True)
    drug_type_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='drug_type_exposures', db_column='drug_type_concept_id')
    stop_reason = models.CharField(max_length=20, null=True, blank=True)
    refills = models.IntegerField(null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    days_supply = models.IntegerField(null=True, blank=True)
    sig = models.TextField(null=True, blank=True)
    route_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='drug_route_exposures', db_column='route_concept_id', null=True, blank=True)
    lot_number = models.CharField(max_length=50, null=True, blank=True)
    provider_id = models.IntegerField(null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.SET_NULL, db_column='visit_occurrence_id', null=True, blank=True)
    visit_detail_id = models.IntegerField(null=True, blank=True)
    drug_source_value = models.CharField(max_length=50, null=True, blank=True)
    drug_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='drug_source_exposures', db_column='drug_source_concept_id', null=True, blank=True)
    route_source_value = models.CharField(max_length=50, null=True, blank=True)
    dose_unit_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'drug_exposure'

    def __str__(self):
        return f"Drug Exposure {self.drug_exposure_id} for Person {self.person_id}"


class Measurement(models.Model):
    """OMOP CDM Measurement table - laboratory tests and vital signs."""
    measurement_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    measurement_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='measurements', db_column='measurement_concept_id')
    measurement_date = models.DateField()
    measurement_datetime = models.DateTimeField(null=True, blank=True)
    measurement_time = models.CharField(max_length=10, null=True, blank=True)
    measurement_type_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='measurement_types', db_column='measurement_type_concept_id')
    operator_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='measurement_operators', db_column='operator_concept_id', null=True, blank=True)
    value_as_number = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    value_as_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='measurement_values', db_column='value_as_concept_id', null=True, blank=True)
    unit_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='measurement_units', db_column='unit_concept_id', null=True, blank=True)
    range_low = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    range_high = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    provider_id = models.IntegerField(null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.SET_NULL, db_column='visit_occurrence_id', null=True, blank=True)
    visit_detail_id = models.IntegerField(null=True, blank=True)
    measurement_source_value = models.CharField(max_length=50, null=True, blank=True)
    measurement_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='measurement_sources', db_column='measurement_source_concept_id', null=True, blank=True)
    unit_source_value = models.CharField(max_length=50, null=True, blank=True)
    unit_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='measurement_unit_sources', db_column='unit_source_concept_id', null=True, blank=True)
    value_source_value = models.CharField(max_length=50, null=True, blank=True)
    measurement_event_id = models.BigIntegerField(null=True, blank=True)
    meas_event_field_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='measurement_event_fields', db_column='meas_event_field_concept_id', null=True, blank=True)

    class Meta:
        db_table = 'measurement'

    def __str__(self):
        return f"Measurement {self.measurement_id} for Person {self.person_id}"


class Observation(models.Model):
    """OMOP CDM Observation table - clinical facts that don't fit other domains."""
    observation_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    observation_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='observations', db_column='observation_concept_id')
    observation_date = models.DateField()
    observation_datetime = models.DateTimeField(null=True, blank=True)
    observation_type_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='observation_types', db_column='observation_type_concept_id')
    value_as_number = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    value_as_string = models.CharField(max_length=60, null=True, blank=True)
    value_as_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='observation_values', db_column='value_as_concept_id', null=True, blank=True)
    qualifier_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='observation_qualifiers', db_column='qualifier_concept_id', null=True, blank=True)
    unit_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='observation_units', db_column='unit_concept_id', null=True, blank=True)
    provider_id = models.IntegerField(null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.SET_NULL, db_column='visit_occurrence_id', null=True, blank=True)
    visit_detail_id = models.IntegerField(null=True, blank=True)
    observation_source_value = models.CharField(max_length=50, null=True, blank=True)
    observation_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='observation_sources', db_column='observation_source_concept_id', null=True, blank=True)
    unit_source_value = models.CharField(max_length=50, null=True, blank=True)
    qualifier_source_value = models.CharField(max_length=50, null=True, blank=True)
    value_source_value = models.CharField(max_length=50, null=True, blank=True)
    observation_event_id = models.BigIntegerField(null=True, blank=True)
    obs_event_field_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='observation_event_fields', db_column='obs_event_field_concept_id', null=True, blank=True)

    class Meta:
        db_table = 'observation'

    def __str__(self):
        return f"Observation {self.observation_id} for Person {self.person_id}"

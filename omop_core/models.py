from django.db import models


class Vocabulary(models.Model):
    """
    VOCABULARY table contains records that uniquely identify the Vocabularies.
    """
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
    """
    DOMAIN table includes a list of OMOP-defined Domains the Concepts of the Vocabulary belong to.
    """
    domain_id = models.CharField(max_length=20, primary_key=True)
    domain_name = models.CharField(max_length=255)
    domain_concept_id = models.IntegerField()

    class Meta:
        db_table = 'domain'

    def __str__(self):
        return f"{self.domain_id}: {self.domain_name}"


class ConceptClass(models.Model):
    """
    CONCEPT_CLASS table is a reference table, which includes a list of the classifications used to differentiate Concepts within a given Vocabulary.
    """
    concept_class_id = models.CharField(max_length=20, primary_key=True)
    concept_class_name = models.CharField(max_length=255)
    concept_class_concept_id = models.IntegerField()

    class Meta:
        db_table = 'concept_class'

    def __str__(self):
        return f"{self.concept_class_id}: {self.concept_class_name}"


class Concept(models.Model):
    """
    CONCEPT table contains records that uniquely identify each fundamental unit of meaning used to represent healthcare information in the OMOP Common Data Model.
    """
    concept_id = models.IntegerField(primary_key=True)
    concept_name = models.CharField(max_length=255)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, db_column='domain_id')
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.CASCADE, db_column='vocabulary_id')
    concept_class = models.ForeignKey(ConceptClass, on_delete=models.CASCADE, db_column='concept_class_id')
    standard_concept = models.CharField(max_length=1, null=True, blank=True)
    concept_code = models.CharField(max_length=50)
    valid_start_date = models.DateField()
    valid_end_date = models.DateField()
    invalid_reason = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        db_table = 'concept'

    def __str__(self):
        return f"{self.concept_id}: {self.concept_name}"


class ConceptRelationship(models.Model):
    """
    CONCEPT_RELATIONSHIP table contains records that define direct relationships between any two Concepts.
    """
    concept_id_1 = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='relationships_as_concept_1', db_column='concept_id_1')
    concept_id_2 = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='relationships_as_concept_2', db_column='concept_id_2')
    relationship_id = models.CharField(max_length=20)
    valid_start_date = models.DateField()
    valid_end_date = models.DateField()
    invalid_reason = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        db_table = 'concept_relationship'
        unique_together = ('concept_id_1', 'concept_id_2', 'relationship_id')

    def __str__(self):
        return f"{self.concept_id_1} {self.relationship_id} {self.concept_id_2}"


class ConceptSynonym(models.Model):
    """
    CONCEPT_SYNONYM table is used to store alternate names and descriptions for Concepts.
    """
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='concept_id')
    concept_synonym_name = models.CharField(max_length=1000)
    language_concept_id = models.IntegerField()

    class Meta:
        db_table = 'concept_synonym'

    def __str__(self):
        return f"{self.concept}: {self.concept_synonym_name}"


class ConceptAncestor(models.Model):
    """
    CONCEPT_ANCESTOR table is designed to simplify observational analysis by providing the complete hierarchical relationships between Concepts.
    """
    ancestor_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='descendant_relationships', db_column='ancestor_concept_id')
    descendant_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='ancestor_relationships', db_column='descendant_concept_id')
    min_levels_of_separation = models.IntegerField()
    max_levels_of_separation = models.IntegerField()

    class Meta:
        db_table = 'concept_ancestor'
        unique_together = ('ancestor_concept', 'descendant_concept')

    def __str__(self):
        return f"{self.ancestor_concept} -> {self.descendant_concept}"


class SourceToConceptMap(models.Model):
    """
    SOURCE_TO_CONCEPT_MAP table is a legacy data structure within the OMOP Common Data Model, recommended for use in ETL processes to maintain local source codes which are not available as Concepts in the Standardized Vocabularies.
    """
    source_code = models.CharField(max_length=50)
    source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='source_mappings', db_column='source_concept_id')
    source_vocabulary_id = models.CharField(max_length=20)
    source_code_description = models.CharField(max_length=255, null=True, blank=True)
    target_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='target_mappings', db_column='target_concept_id')
    target_vocabulary_id = models.CharField(max_length=20)
    valid_start_date = models.DateField()
    valid_end_date = models.DateField()
    invalid_reason = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        db_table = 'source_to_concept_map'

    def __str__(self):
        return f"{self.source_code} -> {self.target_concept}"


class DrugStrength(models.Model):
    """
    DRUG_STRENGTH table contains structured content about the amount or concentration and associated units of a specific ingredient contained within a particular drug product.
    """
    drug_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='drug_strengths', db_column='drug_concept_id')
    ingredient_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='ingredient_strengths', db_column='ingredient_concept_id')
    amount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_unit_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='amount_unit_strengths', db_column='amount_unit_concept_id', null=True, blank=True)
    numerator_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    numerator_unit_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='numerator_unit_strengths', db_column='numerator_unit_concept_id', null=True, blank=True)
    denominator_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    denominator_unit_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='denominator_unit_strengths', db_column='denominator_unit_concept_id', null=True, blank=True)
    box_size = models.IntegerField(null=True, blank=True)
    valid_start_date = models.DateField()
    valid_end_date = models.DateField()
    invalid_reason = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        db_table = 'drug_strength'

    def __str__(self):
        return f"{self.drug_concept} - {self.ingredient_concept}"


class CdmSource(models.Model):
    """
    CDM_SOURCE table contains detail about the source database and the process used to transform the data into the OMOP Common Data Model.
    """
    cdm_source_name = models.CharField(max_length=255)
    cdm_source_abbreviation = models.CharField(max_length=25, null=True, blank=True)
    cdm_holder = models.CharField(max_length=255, null=True, blank=True)
    source_description = models.TextField(null=True, blank=True)
    source_documentation_reference = models.CharField(max_length=255, null=True, blank=True)
    cdm_etl_reference = models.CharField(max_length=255, null=True, blank=True)
    source_release_date = models.DateField(null=True, blank=True)
    cdm_release_date = models.DateField(null=True, blank=True)
    cdm_version = models.CharField(max_length=10, null=True, blank=True)
    cdm_version_concept_id = models.IntegerField(null=True, blank=True)
    vocabulary_version = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'cdm_source'

    def __str__(self):
        return self.cdm_source_name


class Metadata(models.Model):
    """
    METADATA table is a reference table that contains metadata information about a dataset that has been transformed to the OMOP Common Data Model.
    """
    metadata_id = models.AutoField(primary_key=True)
    metadata_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='metadata_concept_id')
    metadata_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='metadata_types', db_column='metadata_type_concept_id')
    name = models.CharField(max_length=250)
    value_as_string = models.TextField(null=True, blank=True)
    value_as_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='metadata_values', db_column='value_as_concept_id', null=True, blank=True)
    value_as_number = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    metadata_date = models.DateField(null=True, blank=True)
    metadata_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'metadata'

    def __str__(self):
        return f"{self.name}: {self.value_as_string or self.value_as_number}"


# Clinical Data Tables

class Location(models.Model):
    """
    LOCATION table represents a generic way to capture physical location or address information of Persons and Care Sites.
    """
    location_id = models.AutoField(primary_key=True)
    address_1 = models.CharField(max_length=50, null=True, blank=True)
    address_2 = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    zip = models.CharField(max_length=9, null=True, blank=True)
    county = models.CharField(max_length=20, null=True, blank=True)
    location_source_value = models.CharField(max_length=50, null=True, blank=True)
    country_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='country_concept_id', null=True, blank=True)
    country_source_value = models.CharField(max_length=80, null=True, blank=True)
    latitude = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True)
    longitude = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True)

    class Meta:
        db_table = 'location'

    def __str__(self):
        return f"{self.city}, {self.state} {self.zip}"


class CareSite(models.Model):
    """
    CARE_SITE table contains a list of uniquely identified institutional (physical or organizational) units where healthcare delivery is practiced (offices, wards, hospitals, clinics, etc.).
    """
    care_site_id = models.AutoField(primary_key=True)
    care_site_name = models.CharField(max_length=255, null=True, blank=True)
    place_of_service_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='place_of_service_concept_id', null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    care_site_source_value = models.CharField(max_length=50, null=True, blank=True)
    place_of_service_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'care_site'

    def __str__(self):
        return self.care_site_name or f"Care Site {self.care_site_id}"


class Provider(models.Model):
    """
    PROVIDER table contains a list of uniquely identified healthcare providers.
    """
    provider_id = models.AutoField(primary_key=True)
    provider_name = models.CharField(max_length=255, null=True, blank=True)
    npi = models.CharField(max_length=20, null=True, blank=True)
    dea = models.CharField(max_length=20, null=True, blank=True)
    specialty_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='specialty_concept_id', null=True, blank=True)
    care_site = models.ForeignKey(CareSite, on_delete=models.CASCADE, null=True, blank=True)
    year_of_birth = models.IntegerField(null=True, blank=True)
    gender_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='provider_gender', db_column='gender_concept_id', null=True, blank=True)
    provider_source_value = models.CharField(max_length=50, null=True, blank=True)
    specialty_source_value = models.CharField(max_length=50, null=True, blank=True)
    specialty_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='provider_specialty_source', db_column='specialty_source_concept_id', null=True, blank=True)
    gender_source_value = models.CharField(max_length=50, null=True, blank=True)
    gender_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='provider_gender_source', db_column='gender_source_concept_id', null=True, blank=True)

    class Meta:
        db_table = 'provider'

    def __str__(self):
        return self.provider_name or f"Provider {self.provider_id}"


class Person(models.Model):
    """
    PERSON table contains records that uniquely identify each patient in the source data who is time at-risk to have clinical observations recorded within the source systems.
    """
    person_id = models.AutoField(primary_key=True)
    gender_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='gender_concept_id')
    year_of_birth = models.IntegerField()
    month_of_birth = models.IntegerField(null=True, blank=True)
    day_of_birth = models.IntegerField(null=True, blank=True)
    birth_datetime = models.DateTimeField(null=True, blank=True)
    race_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='person_race', db_column='race_concept_id')
    ethnicity_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='person_ethnicity', db_column='ethnicity_concept_id')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    care_site = models.ForeignKey(CareSite, on_delete=models.CASCADE, null=True, blank=True)
    person_source_value = models.CharField(max_length=50, null=True, blank=True)
    gender_source_value = models.CharField(max_length=50, null=True, blank=True)
    gender_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='person_gender_source', db_column='gender_source_concept_id', null=True, blank=True)
    race_source_value = models.CharField(max_length=50, null=True, blank=True)
    race_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='person_race_source', db_column='race_source_concept_id', null=True, blank=True)
    ethnicity_source_value = models.CharField(max_length=50, null=True, blank=True)
    ethnicity_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='person_ethnicity_source', db_column='ethnicity_source_concept_id', null=True, blank=True)

    class Meta:
        db_table = 'person'

    def __str__(self):
        return f"Person {self.person_id}"


class ObservationPeriod(models.Model):
    """
    OBSERVATION_PERIOD table contains records which uniquely define the spans of time for which a Person is at-risk to have clinical events recorded.
    """
    observation_period_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    observation_period_start_date = models.DateField()
    observation_period_end_date = models.DateField()
    period_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='period_type_concept_id')

    class Meta:
        db_table = 'observation_period'

    def __str__(self):
        return f"Observation Period {self.observation_period_id} for {self.person}"


class VisitOccurrence(models.Model):
    """
    VISIT_OCCURRENCE table contains the spans of time a Person continuously receives medical services from one or more providers at a Care Site in a given setting within the health care system.
    """
    visit_occurrence_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    visit_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='visit_concept_id')
    visit_start_date = models.DateField()
    visit_start_datetime = models.DateTimeField(null=True, blank=True)
    visit_end_date = models.DateField()
    visit_end_datetime = models.DateTimeField(null=True, blank=True)
    visit_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='visit_types', db_column='visit_type_concept_id')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    care_site = models.ForeignKey(CareSite, on_delete=models.CASCADE, null=True, blank=True)
    visit_source_value = models.CharField(max_length=50, null=True, blank=True)
    visit_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='visit_sources', db_column='visit_source_concept_id', null=True, blank=True)
    admitted_from_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='admitted_from', db_column='admitted_from_concept_id', null=True, blank=True)
    admitted_from_source_value = models.CharField(max_length=50, null=True, blank=True)
    discharged_to_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='discharged_to', db_column='discharged_to_concept_id', null=True, blank=True)
    discharged_to_source_value = models.CharField(max_length=50, null=True, blank=True)
    preceding_visit_occurrence = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'visit_occurrence'

    def __str__(self):
        return f"Visit {self.visit_occurrence_id} for {self.person}"


class VisitDetail(models.Model):
    """
    VISIT_DETAIL table is an optional table used to represents details of each record in the parent VISIT_OCCURRENCE table.
    """
    visit_detail_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    visit_detail_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='visit_detail_concept_id')
    visit_detail_start_date = models.DateField()
    visit_detail_start_datetime = models.DateTimeField(null=True, blank=True)
    visit_detail_end_date = models.DateField()
    visit_detail_end_datetime = models.DateTimeField(null=True, blank=True)
    visit_detail_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='visit_detail_types', db_column='visit_detail_type_concept_id')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    care_site = models.ForeignKey(CareSite, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail_source_value = models.CharField(max_length=50, null=True, blank=True)
    visit_detail_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='visit_detail_sources', db_column='visit_detail_source_concept_id', null=True, blank=True)
    admitted_from_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='visit_detail_admitted_from', db_column='admitted_from_concept_id', null=True, blank=True)
    admitted_from_source_value = models.CharField(max_length=50, null=True, blank=True)
    discharged_to_source_value = models.CharField(max_length=50, null=True, blank=True)
    discharged_to_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='visit_detail_discharged_to', db_column='discharged_to_concept_id', null=True, blank=True)
    preceding_visit_detail = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    parent_visit_detail = models.ForeignKey('self', on_delete=models.CASCADE, related_name='child_visit_details', null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE)

    class Meta:
        db_table = 'visit_detail'

    def __str__(self):
        return f"Visit Detail {self.visit_detail_id} for {self.person}"


# Import all clinical event models
from .clinical_models import *
from .health_system_models import *

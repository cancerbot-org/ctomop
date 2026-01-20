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


class Location(models.Model):
    """OMOP CDM Location table - geographic locations."""
    location_id = models.BigIntegerField(primary_key=True)
    address_1 = models.CharField(max_length=50, null=True, blank=True)
    address_2 = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    zip = models.CharField(max_length=9, null=True, blank=True)
    county = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    location_source_value = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        db_table = 'location'

    def __str__(self):
        return f"Location {self.location_id}: {self.city}, {self.state}, {self.country}"


class Person(models.Model):
    person_id = models.IntegerField(primary_key=True)
    gender_concept = models.ForeignKey(
        Concept, 
        on_delete=models.PROTECT, 
        related_name='person_gender', 
        null=True, 
        blank=True,
        db_column='gender_concept_id'
    )
    year_of_birth = models.IntegerField()
    race_concept = models.ForeignKey(
        Concept, 
        on_delete=models.PROTECT, 
        related_name='person_race', 
        null=True, 
        blank=True,
        db_column='race_concept_id'
    )
    ethnicity_concept = models.ForeignKey(
        Concept, 
        on_delete=models.PROTECT, 
        related_name='person_ethnicity', 
        null=True, 
        blank=True,
        db_column='ethnicity_concept_id'
    )
    
    class Meta:
        db_table = 'person'
    
    def __str__(self):
        return f"Person {self.person_id}"
    
    def get_language_skills_summary(self):
        """Return a dictionary of language skills in format {language_name: skill_level}"""
        skills = {}
        for lang_skill in self.language_skills.all():
            skills[lang_skill.language_concept.concept_name] = lang_skill.skill_level
        return skills
    
    def get_primary_language(self):
        """Return the primary language or None if not set"""
        primary_lang = self.language_skills.filter(is_primary=True).first()
        return primary_lang.language_concept.concept_name if primary_lang else None


class PersonLanguageSkill(models.Model):
    """Language skills for a person - supports multiple languages with different skill levels."""
    
    SKILL_LEVEL_CHOICES = [
        ('speak', 'Speak'),
        ('write', 'Write'),
        ('both', 'Both Speak and Write'),
    ]
    
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='language_skills')
    language_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='person_language_skills', 
                                        db_column='language_concept_id')
    skill_level = models.CharField(max_length=10, choices=SKILL_LEVEL_CHOICES, 
                                  help_text="Language skill level: speak, write, both")
    is_primary = models.BooleanField(default=False, help_text="Is this the person's primary language?")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'person_language_skill'
        unique_together = ['person', 'language_concept']
        indexes = [
            models.Index(fields=['person', 'is_primary']),
        ]

    def __str__(self):
        return f"Person {self.person_id}: {self.language_concept.concept_name} ({self.skill_level})"


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
    value_as_string = models.CharField(max_length=60, null=True, blank=True)
    value_as_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='measurement_values', db_column='value_as_concept_id', null=True, blank=True)
    qualifier_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='measurement_qualifiers', db_column='qualifier_concept_id', null=True, blank=True)
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
    qualifier_source_value = models.CharField(max_length=50, null=True, blank=True)
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


# Choice classes for PatientInfo model
class GenderChoices(models.TextChoices):
    """Gender choices for PatientInfo"""
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    UNKNOWN = 'U', 'Unknown'


class WeightUnits(models.TextChoices):
    """Weight unit choices"""
    KG = 'kg', 'Kilograms'
    LB = 'lb', 'Pounds'


class HeightUnits(models.TextChoices):
    """Height unit choices"""
    CM = 'cm', 'Centimeters'
    IN = 'in', 'Inches'


class HemoglobinUnits(models.TextChoices):
    """Hemoglobin unit choices"""
    G_DL = 'G/DL', 'g/dL'
    G_L = 'G/L', 'g/L'
    MMOL_L = 'MMOL/L', 'mmol/L'


class PlateletCountUnits(models.TextChoices):
    """Platelet count unit choices"""
    CELLS_UL = 'CELLS/UL', '10^3/μL'
    CELLS_L = 'CELLS/L', '10^9/L'


class SerumCalciumUnits(models.TextChoices):
    """Serum calcium unit choices"""
    MG_DL = 'MG/DL', 'mg/dL'
    MMOL_L = 'MMOL/L', 'mmol/L'


class SerumCreatinineUnits(models.TextChoices):
    """Serum creatinine unit choices"""
    MG_DL = 'MG/DL', 'mg/dL'
    UMOL_L = 'UMOL/L', 'μmol/L'


class SerumBilirubinUnits(models.TextChoices):
    """Serum bilirubin unit choices"""
    MG_DL = 'MG/DL', 'mg/dL'
    UMOL_L = 'UMOL/L', 'μmol/L'


class AlbuminUnits(models.TextChoices):
    """Albumin unit choices"""
    G_DL = 'G/DL', 'g/dL'
    G_L = 'G/L', 'g/L'


class PatientInfo(models.Model):
    """
    Comprehensive patient information model adapted from exactomop repository
    Integrated with OMOP CDM Person model for clinical trial matching and research
    """
    # Link to OMOP Person
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='patient_info')
    
    # General Information
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Disease Information
    disease = models.CharField(max_length=100, null=True, blank=True)
    
    # Demographics
    patient_age = models.IntegerField(help_text="What is the patient's age?", blank=True, null=True)
    gender = models.CharField(
        max_length=2,
        choices=GenderChoices.choices,
        blank=True,
        null=True,
        help_text="Patient's gender"
    )
    weight = models.FloatField(help_text="Patient's weight", blank=True, null=True)
    weight_units = models.CharField(
        max_length=2,
        choices=WeightUnits.choices,
        blank=True,
        null=True,
        default='kg',
        help_text="Units for the patient's weight"
    )
    height = models.FloatField(help_text="Patient's height", blank=True, null=True)
    height_units = models.CharField(
        max_length=2,
        choices=HeightUnits.choices,
        blank=True,
        null=True,
        default='cm',
        help_text="Units for the patient's height"
    )
    bmi = models.FloatField(editable=False, help_text="Patient's BMI (computed)", blank=True, null=True)
    ethnicity = models.TextField(blank=True, null=True)
    systolic_blood_pressure = models.IntegerField(help_text="Patient's systolic blood pressure", blank=True, null=True)
    diastolic_blood_pressure = models.IntegerField(help_text="Patient's diastolic blood pressure", blank=True, null=True)

    # Geographic location
    country = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)

    # Disease information
    disease = models.TextField(blank=True, null=True)
    stage = models.TextField(blank=True, null=True)
    karnofsky_performance_score = models.IntegerField(blank=True, null=True, default=100)
    ecog_performance_status = models.IntegerField(blank=True, null=True)
    no_other_active_malignancies = models.BooleanField(blank=False, null=False, default=True)
    no_pre_existing_conditions = models.BooleanField(blank=True, null=True)
    peripheral_neuropathy_grade = models.IntegerField(blank=True, null=True)

    # Cancer-specific fields
    cytogenic_markers = models.TextField(blank=True, null=True)
    molecular_markers = models.TextField(blank=True, null=True)
    stem_cell_transplant_history = models.JSONField(blank=True, null=True, default=list)
    plasma_cell_leukemia = models.BooleanField(blank=True, null=True, default=True)
    progression = models.TextField(blank=True, null=True)

    # Vital signs
    heartrate = models.IntegerField(help_text="Patient's heart rate", blank=True, null=True)
    heartrate_variability = models.IntegerField(help_text="Patient's heart rate variability", blank=True, null=True)

    # Legacy condition codes
    condition_code_icd_10 = models.TextField(blank=True, null=True)
    condition_code_snomed_ct = models.TextField(blank=True, null=True)

    # Treatment history
    prior_therapy = models.TextField(blank=True, null=True)
    first_line_therapy = models.TextField(blank=True, null=True)
    first_line_date = models.DateField(blank=True, null=True)
    first_line_outcome = models.TextField(blank=True, null=True)
    second_line_therapy = models.TextField(blank=True, null=True)
    second_line_date = models.DateField(blank=True, null=True)
    second_line_outcome = models.TextField(blank=True, null=True)
    later_therapy = models.TextField(blank=True, null=True)
    later_date = models.DateField(blank=True, null=True)
    later_outcome = models.TextField(blank=True, null=True)
    supportive_therapies = models.TextField(blank=True, null=True)
    supportive_therapy_date = models.DateField(blank=True, null=True)
    relapse_count = models.IntegerField(blank=True, null=True)
    treatment_refractory_status = models.CharField(max_length=255, blank=True, null=True)

    # Legacy therapy fields
    therapy_lines_count = models.IntegerField(blank=True, null=True)
    line_of_therapy = models.TextField(blank=True, null=True)

    # Blood work with units
    absolute_neutrophile_count = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    absolute_neutrophile_count_units = models.CharField(
        max_length=10,
        choices=PlateletCountUnits.choices,
        blank=True,
        null=True,
        default='CELLS/UL'
    )
    platelet_count = models.IntegerField(blank=True, null=True)
    platelet_count_units = models.CharField(
        max_length=10,
        choices=PlateletCountUnits.choices,
        blank=True,
        null=True,
        default='CELLS/UL'
    )
    white_blood_cell_count = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    white_blood_cell_count_units = models.CharField(
        max_length=10,
        choices=PlateletCountUnits.choices,
        blank=True,
        null=True,
        default='CELLS/L'
    )
    red_blood_cell_count = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    red_blood_cell_count_units = models.CharField(
        max_length=10,
        choices=PlateletCountUnits.choices,
        blank=True,
        null=True,
        default='CELLS/L'
    )

    serum_calcium_level = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    serum_calcium_level_units = models.CharField(
        max_length=15,
        choices=SerumCalciumUnits.choices,
        blank=True,
        null=True,
        default='MG/DL'
    )
    creatinine_clearance_rate = models.IntegerField(blank=True, null=True)
    serum_creatinine_level = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    serum_creatinine_level_units = models.CharField(
        max_length=15,
        choices=SerumCreatinineUnits.choices,
        blank=True,
        null=True,
        default='MG/DL'
    )
    hemoglobin_level = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    hemoglobin_level_units = models.CharField(
        max_length=10,
        choices=HemoglobinUnits.choices,
        blank=True,
        null=True,
        default='G/DL'
    )

    # Additional lab values
    bone_lesions = models.TextField(blank=True, null=True)
    meets_crab = models.BooleanField(blank=True, null=True)
    estimated_glomerular_filtration_rate = models.IntegerField(blank=True, null=True)
    renal_adequacy_status = models.BooleanField(blank=True, null=True)
    liver_enzyme_levels_ast = models.IntegerField(blank=True, null=True)
    liver_enzyme_levels_alt = models.IntegerField(blank=True, null=True)
    liver_enzyme_levels_alp = models.IntegerField(blank=True, null=True)
    serum_bilirubin_level_total = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    serum_bilirubin_level_total_units = models.CharField(
        max_length=15,
        choices=SerumBilirubinUnits.choices,
        blank=True,
        null=True,
        default='MG/DL'
    )
    serum_bilirubin_level_direct = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    serum_bilirubin_level_direct_units = models.CharField(
        max_length=15,
        choices=SerumBilirubinUnits.choices,
        blank=True,
        null=True,
        default='MG/DL'
    )
    albumin_level = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    albumin_level_units = models.CharField(
        max_length=15,
        choices=AlbuminUnits.choices,
        blank=True,
        null=True,
        default='G/DL'
    )
    kappa_flc = models.IntegerField(blank=True, null=True)
    lambda_flc = models.IntegerField(blank=True, null=True)
    meets_slim = models.BooleanField(blank=True, null=True)

    # Legacy blood work fields
    liver_enzyme_levels = models.IntegerField(blank=True, null=True)
    serum_bilirubin_level = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)

    # Laboratory results
    monoclonal_protein_serum = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    monoclonal_protein_urine = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    lactate_dehydrogenase_level = models.IntegerField(blank=True, null=True)
    pulmonary_function_test_result = models.BooleanField(blank=False, null=False, default=False)
    bone_imaging_result = models.BooleanField(blank=False, null=False, default=False)
    clonal_plasma_cells = models.IntegerField(blank=True, null=True)
    ejection_fraction = models.IntegerField(blank=True, null=True)

    # Behavioral and risk factors
    consent_capability = models.BooleanField(help_text="Does the patient have cognitive ability to consent?", blank=False, null=False, default=True)
    caregiver_availability_status = models.BooleanField(help_text="Is there an available caregiver for the patient?", blank=False, null=False, default=False)
    contraceptive_use = models.BooleanField(help_text="Does the patient use contraceptives?", blank=False, null=False, default=False)
    no_pregnancy_or_lactation_status = models.BooleanField(help_text="Does the patient self assess as not pregnant or lactating?", blank=False, null=False, default=True)
    pregnancy_test_result = models.BooleanField(help_text="Does the female patient of childbearing age have a negative test result for pregnancy?", blank=False, null=False, default=False)
    no_mental_health_disorder_status = models.BooleanField(help_text="Does the patient have a mental health disorder?", blank=False, null=False, default=True)
    no_concomitant_medication_status = models.BooleanField(help_text="Does the patient have concomitant medication?", blank=False, null=False, default=True)
    concomitant_medication_details = models.CharField(max_length=255, help_text="Details about the patient's concomitant medications", blank=True, null=True)

    no_tobacco_use_status = models.BooleanField(help_text="Does the patient use tobacco?", blank=False, null=False, default=True)
    tobacco_use_details = models.CharField(max_length=255, help_text="Details about the patient's tobacco use", blank=True, null=True)
    no_substance_use_status = models.BooleanField(help_text="Does the patient use substances?", blank=False, null=False, default=True)
    substance_use_details = models.CharField(max_length=255, help_text="Details about the patient's substance use", blank=True, null=True)
    no_geographic_exposure_risk = models.BooleanField(help_text="Has the patient had geographic exposure to risk?", blank=False, null=False, default=True)
    geographic_exposure_risk_details = models.CharField(max_length=255, help_text="Details about the patient's geographic exposure risk", blank=True, null=True)

    no_hiv_status = models.BooleanField(help_text="Does the patient has had HIV?", blank=False, null=False, default=True)
    no_hepatitis_b_status = models.BooleanField(help_text="Does the patient has had Hepatitis B (HBV)?", blank=False, null=False, default=True)
    no_hepatitis_c_status = models.BooleanField(help_text="Does the patient has had Hepatitis C (HCV)?", blank=False, null=False, default=True)
    no_active_infection_status = models.BooleanField(help_text="Does the patient has any active infection?", blank=False, null=False, default=True)

    concomitant_medications = models.TextField(blank=True, null=True)
    concomitant_medication_date = models.DateField(blank=True, null=True)

    # Remission and washout periods
    remission_duration_min = models.TextField(blank=True, null=True)
    washout_period_duration = models.TextField(blank=True, null=True)

    # Viral infection status
    hiv_status = models.BooleanField(blank=True, null=True)
    hepatitis_b_status = models.BooleanField(blank=True, null=True)
    hepatitis_c_status = models.BooleanField(blank=True, null=True)

    # Treatment dates
    last_treatment = models.DateField(help_text="Date and time of the last treatment", blank=True, null=True)

    # Breast cancer specific fields
    bone_only_metastasis_status = models.BooleanField(blank=True, null=True)
    menopausal_status = models.TextField(blank=True, null=True)
    metastatic_status = models.BooleanField(blank=True, null=True)
    toxicity_grade = models.IntegerField(blank=True, null=True)
    planned_therapies = models.TextField(blank=True, null=True)

    # Biopsy results
    histologic_type = models.TextField(blank=True, null=True)
    biopsy_grade_depr = models.TextField(blank=True, null=True)
    biopsy_grade = models.IntegerField(blank=True, null=True)
    measurable_disease_by_recist_status = models.BooleanField(blank=True, null=True)
    estrogen_receptor_status = models.TextField(blank=True, null=True)
    progesterone_receptor_status = models.TextField(blank=True, null=True)
    her2_status = models.TextField(blank=True, null=True)
    tnbc_status = models.BooleanField(blank=True, null=True)
    hrd_status = models.TextField(blank=True, null=True)
    hr_status = models.TextField(blank=True, null=True)

    tumor_stage = models.TextField(blank=True, null=True)
    nodes_stage = models.TextField(blank=True, null=True)
    distant_metastasis_stage = models.TextField(blank=True, null=True)
    staging_modalities = models.TextField(blank=True, null=True)

    # Genetic mutations
    genetic_mutations = models.JSONField(blank=True, null=False, default=list)

    # PD-L1 and biomarkers
    pd_l1_tumor_cels = models.IntegerField(blank=True, null=True)
    pd_l1_assay = models.TextField(blank=True, null=True)
    pd_l1_ic_percentage = models.IntegerField(blank=True, null=True)
    pd_l1_combined_positive_score = models.IntegerField(blank=True, null=True)
    ki67_proliferation_index = models.IntegerField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "patient_info"
        indexes = [
            models.Index(fields=["person"]),
            models.Index(fields=["patient_age"]),
            models.Index(fields=["disease"]),
            models.Index(fields=["stage"]),
        ]

    def __str__(self):
        return f"PatientInfo for Person {self.person.person_id} (age={self.patient_age}, gender={self.gender})"

    def get_languages(self):
        """Return a dictionary of languages and their skill levels"""
        return self.person.get_language_skills_summary()
    
    def get_primary_language(self):
        """Return the primary language"""
        return self.person.get_primary_language()
    
    def get_languages_display(self):
        """Return a human-readable string of languages and skills like 'English: speak, Spanish: both'"""
        skills = self.get_languages()
        if not skills:
            return "No languages recorded"
        
        display_parts = []
        for language, skill in skills.items():
            display_parts.append(f"{language}: {skill}")
        return ", ".join(display_parts)

    def save(self, *args, **kwargs):
        """Calculate BMI when saving if weight and height are provided"""
        if self.weight and self.height:
            # Convert to metric units for calculation
            weight_kg = self.weight
            height_m = self.height
            
            if self.weight_units == 'lb':
                weight_kg = self.weight * 0.453592
            
            if self.height_units == 'in':
                height_m = self.height * 0.0254
            elif self.height_units == 'cm':
                height_m = self.height / 100
            
            self.bmi = round(weight_kg / (height_m ** 2), 2)
        
        super().save(*args, **kwargs)

from django.db import models
from omop_core.models import Person, Concept, VisitOccurrence


class Episode(models.Model):
    """OMOP Oncology Extension Episode table - disease episodes for cancer patients."""
    episode_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    episode_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='episodes', db_column='episode_concept_id')
    episode_start_date = models.DateField()
    episode_start_datetime = models.DateTimeField(null=True, blank=True)
    episode_end_date = models.DateField(null=True, blank=True)
    episode_end_datetime = models.DateTimeField(null=True, blank=True)
    episode_parent_id = models.IntegerField(null=True, blank=True)
    episode_number = models.IntegerField(null=True, blank=True)
    episode_object_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='episode_objects', db_column='episode_object_concept_id')
    episode_type_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='episode_types', db_column='episode_type_concept_id')
    episode_source_value = models.CharField(max_length=50, null=True, blank=True)
    episode_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='episode_sources', db_column='episode_source_concept_id', null=True, blank=True)

    class Meta:
        db_table = 'episode'

    def __str__(self):
        return f"Episode {self.episode_id} for Person {self.person_id}"


class EpisodeEvent(models.Model):
    """OMOP Oncology Extension Episode Event table - linking clinical events to episodes."""
    episode_id = models.BigIntegerField()
    event_id = models.BigIntegerField()
    episode_event_field_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, db_column='episode_event_field_concept_id')

    class Meta:
        db_table = 'episode_event'
        unique_together = ['episode_id', 'event_id', 'episode_event_field_concept']

    def __str__(self):
        return f"Episode {self.episode_id} Event {self.event_id}"


class CancerModifier(models.Model):
    """OMOP Oncology Extension Cancer Modifier table - cancer-specific modifiers."""
    cancer_modifier_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    cancer_modifier_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='cancer_modifiers', db_column='cancer_modifier_concept_id')
    cancer_modifier_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='cancer_modifier_sources', db_column='cancer_modifier_source_concept_id', null=True, blank=True)
    cancer_modifier_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'cancer_modifier'

    def __str__(self):
        return f"Cancer Modifier {self.cancer_modifier_id} for Person {self.person_id}"


class StemTable(models.Model):
    """OMOP Oncology Extension Stem Table - pre-processing staging table."""
    domain_id = models.CharField(max_length=20)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.SET_NULL, db_column='visit_occurrence_id', null=True, blank=True)
    visit_detail_id = models.IntegerField(null=True, blank=True)
    provider_id = models.IntegerField(null=True, blank=True)
    id = models.BigIntegerField(primary_key=True)
    concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='stem_concepts', db_column='concept_id')
    source_value = models.CharField(max_length=50, null=True, blank=True)
    source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='stem_source_concepts', db_column='source_concept_id', null=True, blank=True)
    type_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='stem_type_concepts', db_column='type_concept_id')
    start_date = models.DateField()
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    verbatim_end_date = models.DateField(null=True, blank=True)
    days_supply = models.IntegerField(null=True, blank=True)
    dose_unit_source_value = models.CharField(max_length=50, null=True, blank=True)
    lot_number = models.CharField(max_length=50, null=True, blank=True)
    modifier_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='stem_modifier_concepts', db_column='modifier_concept_id', null=True, blank=True)
    modifier_source_value = models.CharField(max_length=50, null=True, blank=True)
    operator_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='stem_operator_concepts', db_column='operator_concept_id', null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    range_high = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    range_low = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    refills = models.IntegerField(null=True, blank=True)
    route_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='stem_route_concepts', db_column='route_concept_id', null=True, blank=True)
    route_source_value = models.CharField(max_length=50, null=True, blank=True)
    sig = models.TextField(null=True, blank=True)
    stop_reason = models.CharField(max_length=20, null=True, blank=True)
    unique_device_id = models.CharField(max_length=255, null=True, blank=True)
    unit_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='stem_unit_concepts', db_column='unit_concept_id', null=True, blank=True)
    unit_source_value = models.CharField(max_length=50, null=True, blank=True)
    value_as_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='stem_value_concepts', db_column='value_as_concept_id', null=True, blank=True)
    value_as_number = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    value_as_string = models.CharField(max_length=60, null=True, blank=True)
    value_source_value = models.CharField(max_length=50, null=True, blank=True)
    anatomic_site_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='stem_anatomic_site_concepts', db_column='anatomic_site_concept_id', null=True, blank=True)
    disease_status_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='stem_disease_status_concepts', db_column='disease_status_concept_id', null=True, blank=True)
    specimen_source = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='stem_specimen_source_concepts', db_column='specimen_source_id', null=True, blank=True)
    tumor_grade_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='stem_tumor_grade_concepts', db_column='tumor_grade_concept_id', null=True, blank=True)
    tumor_stage_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='stem_tumor_stage_concepts', db_column='tumor_stage_concept_id', null=True, blank=True)

    class Meta:
        db_table = 'stem_table'

    def __str__(self):
        return f"Stem {self.id} for Person {self.person_id}"


class Histology(models.Model):
    """OMOP Oncology Extension Histology table - cancer histology information."""
    histology_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='histology_concepts', db_column='concept_id')
    histology_date = models.DateField()
    histology_datetime = models.DateTimeField(null=True, blank=True)
    histology_type_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='histology_types', db_column='histology_type_concept_id')
    modifier_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='histology_modifiers', db_column='modifier_concept_id', null=True, blank=True)
    primary_site_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='histology_primary_sites', db_column='primary_site_concept_id', null=True, blank=True)
    lateral_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='histology_laterals', db_column='lateral_concept_id', null=True, blank=True)
    episode_id = models.BigIntegerField(null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.SET_NULL, db_column='visit_occurrence_id', null=True, blank=True)
    histology_source_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='histology_source_concepts', db_column='histology_source_concept_id', null=True, blank=True)
    histology_source_value = models.CharField(max_length=50, null=True, blank=True)
    modifier_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'histology'

    def __str__(self):
        return f"Histology {self.histology_id} for Person {self.person_id}"


class TreatmentLine(models.Model):
    """Treatment line tracking for oncology patients"""
    treatment_line_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    line_number = models.IntegerField(help_text="Treatment line number (1, 2, 3, etc.)")
    line_start_date = models.DateField(help_text="Start date of treatment line")
    line_end_date = models.DateField(null=True, blank=True, help_text="End date of treatment line")
    
    # Treatment details
    treatment_intent = models.CharField(max_length=30, choices=[
        ('CURATIVE', 'Curative'),
        ('PALLIATIVE', 'Palliative'),
        ('ADJUVANT', 'Adjuvant'),
        ('NEOADJUVANT', 'Neoadjuvant'),
        ('MAINTENANCE', 'Maintenance')
    ], help_text="Intent of treatment")
    
    regimen_name = models.CharField(max_length=200, null=True, blank=True, help_text="Treatment regimen name")
    treatment_setting = models.CharField(max_length=20, choices=[
        ('INPATIENT', 'Inpatient'),
        ('OUTPATIENT', 'Outpatient'),
        ('CLINICAL_TRIAL', 'Clinical Trial')
    ], null=True, blank=True)
    
    # Treatment classification
    is_platinum_based = models.BooleanField(default=False)
    is_immunotherapy = models.BooleanField(default=False)
    is_targeted_therapy = models.BooleanField(default=False)
    is_hormone_therapy = models.BooleanField(default=False)
    is_chemotherapy = models.BooleanField(default=False)
    
    # Outcomes
    best_response = models.CharField(max_length=20, choices=[
        ('CR', 'Complete Response'),
        ('PR', 'Partial Response'),
        ('SD', 'Stable Disease'),
        ('PD', 'Progressive Disease'),
        ('NE', 'Not Evaluable')
    ], null=True, blank=True)
    
    treatment_outcome = models.CharField(max_length=30, choices=[
        ('COMPLETED', 'Completed as Planned'),
        ('PROGRESSION', 'Disease Progression'),
        ('TOXICITY', 'Unacceptable Toxicity'),
        ('PATIENT_CHOICE', 'Patient Choice'),
        ('DEATH', 'Death'),
        ('OTHER', 'Other')
    ], null=True, blank=True)
    
    # Performance status at start
    ecog_at_start = models.IntegerField(null=True, blank=True, help_text="ECOG PS at treatment start")
    karnofsky_at_start = models.IntegerField(null=True, blank=True, help_text="Karnofsky score at treatment start")
    
    class Meta:
        db_table = 'treatment_line'
        unique_together = ['person', 'line_number']

    def __str__(self):
        return f"Treatment Line {self.line_number} for Person {self.person_id}"


class SocialDeterminant(models.Model):
    """Social determinants of health"""
    social_determinant_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    determinant_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='social_determinants',
                                          db_column='determinant_concept_id')
    assessment_date = models.DateField()
    assessment_datetime = models.DateTimeField(null=True, blank=True)
    
    # Determinant categories
    determinant_category = models.CharField(max_length=50, choices=[
        ('HOUSING', 'Housing Status'),
        ('EDUCATION', 'Education'),
        ('EMPLOYMENT', 'Employment'),
        ('INCOME', 'Income/Financial'),
        ('INSURANCE', 'Insurance Coverage'),
        ('TRANSPORTATION', 'Transportation'),
        ('SOCIAL_SUPPORT', 'Social Support'),
        ('CAREGIVER', 'Caregiver Status'),
        ('LANGUAGE', 'Language/Communication'),
        ('GEOGRAPHIC', 'Geographic Exposure'),
        ('OTHER', 'Other')
    ])
    
    # Values
    value_as_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='social_determinant_values',
                                       db_column='value_as_concept_id', null=True, blank=True)
    value_as_string = models.CharField(max_length=255, null=True, blank=True)
    value_as_boolean = models.BooleanField(null=True, blank=True)
    
    # Additional details
    assessment_details = models.TextField(null=True, blank=True)
    risk_level = models.CharField(max_length=20, choices=[
        ('HIGH', 'High Risk'),
        ('MODERATE', 'Moderate Risk'),
        ('LOW', 'Low Risk'),
        ('NONE', 'No Risk')
    ], null=True, blank=True)
    
    class Meta:
        db_table = 'social_determinant'

    def __str__(self):
        return f"Social Determinant {self.determinant_category} for Person {self.person_id}"


class HealthBehavior(models.Model):
    """Health behaviors (smoking, alcohol, substance use, etc.)"""
    health_behavior_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    behavior_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='health_behaviors',
                                       db_column='behavior_concept_id')
    assessment_date = models.DateField()
    assessment_datetime = models.DateTimeField(null=True, blank=True)
    
    # Behavior categories
    behavior_type = models.CharField(max_length=30, choices=[
        ('TOBACCO_USE', 'Tobacco Use'),
        ('ALCOHOL_USE', 'Alcohol Use'),
        ('SUBSTANCE_USE', 'Substance Use'),
        ('PHYSICAL_ACTIVITY', 'Physical Activity'),
        ('DIET', 'Diet/Nutrition'),
        ('SEXUAL_BEHAVIOR', 'Sexual Behavior'),
        ('OTHER', 'Other Behavior')
    ])
    
    # Status values
    current_status = models.CharField(max_length=20, choices=[
        ('CURRENT', 'Current User'),
        ('FORMER', 'Former User'),
        ('NEVER', 'Never Used'),
        ('UNKNOWN', 'Unknown')
    ], null=True, blank=True)
    
    # Frequency/amount
    frequency = models.CharField(max_length=50, null=True, blank=True, help_text="Usage frequency")
    amount_per_day = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    amount_unit = models.CharField(max_length=20, null=True, blank=True)
    duration_years = models.IntegerField(null=True, blank=True, help_text="Duration of use in years")
    
    # Cessation information
    quit_date = models.DateField(null=True, blank=True)
    cessation_attempts = models.IntegerField(null=True, blank=True)
    
    # Additional details
    behavior_details = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'health_behavior'

    def __str__(self):
        return f"Health Behavior {self.behavior_type} for Person {self.person_id}"


class InfectionStatus(models.Model):
    """Infection status tracking (HIV, Hepatitis, etc.)"""
    infection_status_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    infection_concept = models.ForeignKey(Concept, on_delete=models.PROTECT, related_name='infection_statuses',
                                        db_column='infection_concept_id')
    assessment_date = models.DateField()
    assessment_datetime = models.DateTimeField(null=True, blank=True)
    
    # Infection type
    infection_type = models.CharField(max_length=30, choices=[
        ('HIV', 'HIV'),
        ('HEPATITIS_B', 'Hepatitis B'),
        ('HEPATITIS_C', 'Hepatitis C'),
        ('TB', 'Tuberculosis'),
        ('COVID_19', 'COVID-19'),
        ('OTHER_VIRAL', 'Other Viral'),
        ('BACTERIAL', 'Bacterial'),
        ('FUNGAL', 'Fungal'),
        ('OTHER', 'Other')
    ])
    
    # Status
    infection_status = models.CharField(max_length=20, choices=[
        ('POSITIVE', 'Positive'),
        ('NEGATIVE', 'Negative'),
        ('INDETERMINATE', 'Indeterminate'),
        ('UNKNOWN', 'Unknown'),
        ('IMMUNE', 'Immune/Vaccinated'),
        ('RESOLVED', 'Resolved')
    ])
    
    # Test details
    test_method = models.CharField(max_length=100, null=True, blank=True)
    test_result_value = models.CharField(max_length=100, null=True, blank=True)
    viral_load = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    viral_load_unit = models.CharField(max_length=20, null=True, blank=True)
    
    # Clinical significance
    is_active_infection = models.BooleanField(null=True, blank=True)
    treatment_required = models.BooleanField(null=True, blank=True)
    
    class Meta:
        db_table = 'infection_status'

    def __str__(self):
        return f"Infection Status {self.infection_type} for Person {self.person_id}"

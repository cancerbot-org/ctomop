from django.db import models
from .models import Concept, Person, VisitOccurrence, VisitDetail, Provider


class PayerPlanPeriod(models.Model):
    """
    PAYER_PLAN_PERIOD table captures details of the period of time that a Person is continuously enrolled under a specific health Plan benefit structure from a given Payer.
    """
    payer_plan_period_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    payer_plan_period_start_date = models.DateField()
    payer_plan_period_end_date = models.DateField()
    payer_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='payer_plans', db_column='payer_concept_id', null=True, blank=True)
    payer_source_value = models.CharField(max_length=50, null=True, blank=True)
    payer_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='payer_sources', db_column='payer_source_concept_id', null=True, blank=True)
    plan_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='plan_concepts', db_column='plan_concept_id', null=True, blank=True)
    plan_source_value = models.CharField(max_length=50, null=True, blank=True)
    plan_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='plan_sources', db_column='plan_source_concept_id', null=True, blank=True)
    sponsor_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='sponsor_concepts', db_column='sponsor_concept_id', null=True, blank=True)
    sponsor_source_value = models.CharField(max_length=50, null=True, blank=True)
    sponsor_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='sponsor_sources', db_column='sponsor_source_concept_id', null=True, blank=True)
    family_source_value = models.CharField(max_length=50, null=True, blank=True)
    stop_reason_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='stop_reasons', db_column='stop_reason_concept_id', null=True, blank=True)
    stop_reason_source_value = models.CharField(max_length=50, null=True, blank=True)
    stop_reason_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='stop_reason_sources', db_column='stop_reason_source_concept_id', null=True, blank=True)

    class Meta:
        db_table = 'payer_plan_period'

    def __str__(self):
        return f"Payer Plan Period {self.payer_plan_period_id} for {self.person}"


class Cost(models.Model):
    """
    COST table captures records containing the cost of any medical entity recorded in one of the OMOP clinical event tables.
    """
    cost_id = models.AutoField(primary_key=True)
    cost_event_id = models.IntegerField()
    cost_domain_id = models.CharField(max_length=20)
    cost_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='cost_type_concept_id')
    currency_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='cost_currencies', db_column='currency_concept_id', null=True, blank=True)
    total_charge = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_paid = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    paid_by_payer = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    paid_by_patient = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    paid_patient_copay = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    paid_patient_coinsurance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    paid_patient_deductible = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    paid_by_primary = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    paid_ingredient_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    paid_dispensing_fee = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    payer_plan_period = models.ForeignKey(PayerPlanPeriod, on_delete=models.CASCADE, null=True, blank=True)
    amount_allowed = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    revenue_code_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='revenue_codes', db_column='revenue_code_concept_id', null=True, blank=True)
    revenue_code_source_value = models.CharField(max_length=50, null=True, blank=True)
    drg_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='drg_concepts', db_column='drg_concept_id', null=True, blank=True)
    drg_source_value = models.CharField(max_length=3, null=True, blank=True)

    class Meta:
        db_table = 'cost'

    def __str__(self):
        return f"Cost {self.cost_id} - {self.cost_domain_id} {self.cost_event_id}"


class DoseEra(models.Model):
    """
    DOSE_ERA table is derived from DRUG_EXPOSURE and represents drug exposure periods that are aggregated by dosage.
    """
    dose_era_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    drug_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='drug_concept_id')
    unit_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='dose_era_units', db_column='unit_concept_id')
    dose_value = models.DecimalField(max_digits=10, decimal_places=2)
    dose_era_start_date = models.DateField()
    dose_era_end_date = models.DateField()

    class Meta:
        db_table = 'dose_era'

    def __str__(self):
        return f"Dose Era {self.dose_era_id} for {self.person}"


class DrugEra(models.Model):
    """
    DRUG_ERA table is derived from DRUG_EXPOSURE and represents drug exposure periods that are aggregated by active ingredient.
    """
    drug_era_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    drug_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='drug_concept_id')
    drug_era_start_date = models.DateField()
    drug_era_end_date = models.DateField()
    drug_exposure_count = models.IntegerField(null=True, blank=True)
    gap_days = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'drug_era'

    def __str__(self):
        return f"Drug Era {self.drug_era_id} for {self.person}"


class ConditionEra(models.Model):
    """
    CONDITION_ERA table is derived from CONDITION_OCCURRENCE and represents condition periods that are aggregated into a single era.
    """
    condition_era_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    condition_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='condition_concept_id')
    condition_era_start_date = models.DateField()
    condition_era_end_date = models.DateField()
    condition_occurrence_count = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'condition_era'

    def __str__(self):
        return f"Condition Era {self.condition_era_id} for {self.person}"


class Cohort(models.Model):
    """
    COHORT table contains records of subjects that satisfy a given set of criteria for a duration of time.
    """
    cohort_definition_id = models.IntegerField()
    subject_id = models.IntegerField()
    cohort_start_date = models.DateField()
    cohort_end_date = models.DateField()

    class Meta:
        db_table = 'cohort'

    def __str__(self):
        return f"Cohort {self.cohort_definition_id} - Subject {self.subject_id}"


class CohortAttribute(models.Model):
    """
    COHORT_ATTRIBUTE table contains attributes associated with each subject within a cohort.
    """
    cohort_definition_id = models.IntegerField()
    subject_id = models.IntegerField()
    cohort_start_date = models.DateField()
    cohort_end_date = models.DateField()
    attribute_definition_id = models.IntegerField()
    value_as_number = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    value_as_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'cohort_attribute'

    def __str__(self):
        return f"Cohort Attribute {self.cohort_definition_id} - {self.attribute_definition_id}"
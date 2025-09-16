from django.db import models
from omop_core.models import Concept, Person, VisitOccurrence, VisitDetail, Provider, CareSite


class Episode(models.Model):
    """
    EPISODE table aggregates lower-level clinical events (VISIT_OCCURRENCE, DRUG_EXPOSURE, PROCEDURE_OCCURRENCE, DEVICE_EXPOSURE) into a higher-level abstraction representing clinically and analytically relevant disease phases, treatment cycles, or care plans.
    """
    episode_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    episode_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='episode_concept_id')
    episode_start_date = models.DateField()
    episode_start_datetime = models.DateTimeField(null=True, blank=True)
    episode_end_date = models.DateField(null=True, blank=True)
    episode_end_datetime = models.DateTimeField(null=True, blank=True)
    episode_parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    episode_number = models.IntegerField(null=True, blank=True)
    episode_object_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='episode_objects', db_column='episode_object_concept_id')
    episode_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='episode_types', db_column='episode_type_concept_id')
    episode_source_value = models.CharField(max_length=50, null=True, blank=True)
    episode_source_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='episode_sources', db_column='episode_source_concept_id', null=True, blank=True)

    class Meta:
        db_table = 'episode'

    def __str__(self):
        return f"Episode {self.episode_id} for {self.person}"


class EpisodeEvent(models.Model):
    """
    EPISODE_EVENT table connects qualifying clinical events (VISIT_OCCURRENCE, DRUG_EXPOSURE, PROCEDURE_OCCURRENCE, DEVICE_EXPOSURE) to the appropriate EPISODE entry.
    """
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    event_id = models.IntegerField()
    episode_event_field_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='episode_event_field_concept_id')

    class Meta:
        db_table = 'episode_event'
        unique_together = ('episode', 'event_id', 'episode_event_field_concept')

    def __str__(self):
        return f"Episode Event {self.episode} - {self.event_id}"


class CancerDiagnosis(models.Model):
    """
    CANCER_DIAGNOSIS table captures cancer-specific diagnosis information including staging, histology, and primary site.
    """
    cancer_diagnosis_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    cancer_diagnosis_date = models.DateField()
    cancer_diagnosis_datetime = models.DateTimeField(null=True, blank=True)
    primary_site_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='cancer_primary_sites', db_column='primary_site_concept_id', null=True, blank=True)
    histology_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='cancer_histologies', db_column='histology_concept_id', null=True, blank=True)
    behavior_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='cancer_behaviors', db_column='behavior_concept_id', null=True, blank=True)
    grade_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='cancer_grades', db_column='grade_concept_id', null=True, blank=True)
    laterality_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='cancer_lateralities', db_column='laterality_concept_id', null=True, blank=True)
    tnm_clinical_t_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='tnm_clinical_t', db_column='tnm_clinical_t_concept_id', null=True, blank=True)
    tnm_clinical_n_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='tnm_clinical_n', db_column='tnm_clinical_n_concept_id', null=True, blank=True)
    tnm_clinical_m_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='tnm_clinical_m', db_column='tnm_clinical_m_concept_id', null=True, blank=True)
    tnm_pathological_t_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='tnm_pathological_t', db_column='tnm_pathological_t_concept_id', null=True, blank=True)
    tnm_pathological_n_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='tnm_pathological_n', db_column='tnm_pathological_n_concept_id', null=True, blank=True)
    tnm_pathological_m_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='tnm_pathological_m', db_column='tnm_pathological_m_concept_id', null=True, blank=True)
    overall_stage_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='cancer_overall_stages', db_column='overall_stage_concept_id', null=True, blank=True)
    ajcc_version_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='ajcc_versions', db_column='ajcc_version_concept_id', null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    cancer_diagnosis_source_value = models.CharField(max_length=50, null=True, blank=True)
    primary_site_source_value = models.CharField(max_length=50, null=True, blank=True)
    histology_source_value = models.CharField(max_length=50, null=True, blank=True)
    behavior_source_value = models.CharField(max_length=50, null=True, blank=True)
    grade_source_value = models.CharField(max_length=50, null=True, blank=True)
    laterality_source_value = models.CharField(max_length=50, null=True, blank=True)
    tnm_clinical_t_source_value = models.CharField(max_length=50, null=True, blank=True)
    tnm_clinical_n_source_value = models.CharField(max_length=50, null=True, blank=True)
    tnm_clinical_m_source_value = models.CharField(max_length=50, null=True, blank=True)
    tnm_pathological_t_source_value = models.CharField(max_length=50, null=True, blank=True)
    tnm_pathological_n_source_value = models.CharField(max_length=50, null=True, blank=True)
    tnm_pathological_m_source_value = models.CharField(max_length=50, null=True, blank=True)
    overall_stage_source_value = models.CharField(max_length=50, null=True, blank=True)
    ajcc_version_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'cancer_diagnosis'

    def __str__(self):
        return f"Cancer Diagnosis {self.cancer_diagnosis_id} for {self.person}"


class CancerTreatment(models.Model):
    """
    CANCER_TREATMENT table captures cancer-specific treatment information including treatment types, intent, and outcomes.
    """
    cancer_treatment_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    cancer_diagnosis = models.ForeignKey(CancerDiagnosis, on_delete=models.CASCADE, null=True, blank=True)
    treatment_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='treatment_concept_id')
    treatment_start_date = models.DateField()
    treatment_start_datetime = models.DateTimeField(null=True, blank=True)
    treatment_end_date = models.DateField(null=True, blank=True)
    treatment_end_datetime = models.DateTimeField(null=True, blank=True)
    treatment_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='treatment_types', db_column='treatment_type_concept_id')
    treatment_intent_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='treatment_intents', db_column='treatment_intent_concept_id', null=True, blank=True)
    treatment_outcome_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='treatment_outcomes', db_column='treatment_outcome_concept_id', null=True, blank=True)
    line_of_therapy = models.IntegerField(null=True, blank=True)
    regimen_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='treatment_regimens', db_column='regimen_concept_id', null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    treatment_source_value = models.CharField(max_length=50, null=True, blank=True)
    treatment_type_source_value = models.CharField(max_length=50, null=True, blank=True)
    treatment_intent_source_value = models.CharField(max_length=50, null=True, blank=True)
    treatment_outcome_source_value = models.CharField(max_length=50, null=True, blank=True)
    regimen_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'cancer_treatment'

    def __str__(self):
        return f"Cancer Treatment {self.cancer_treatment_id} for {self.person}"


class CancerSurgery(models.Model):
    """
    CANCER_SURGERY table captures cancer-specific surgical information including surgical procedures, margins, and lymph node assessment.
    """
    cancer_surgery_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    cancer_diagnosis = models.ForeignKey(CancerDiagnosis, on_delete=models.CASCADE, null=True, blank=True)
    surgery_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='surgery_concept_id')
    surgery_date = models.DateField()
    surgery_datetime = models.DateTimeField(null=True, blank=True)
    surgery_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='surgery_types', db_column='surgery_type_concept_id')
    surgical_margin_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='surgical_margins', db_column='surgical_margin_concept_id', null=True, blank=True)
    residual_disease_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='residual_diseases', db_column='residual_disease_concept_id', null=True, blank=True)
    lymph_nodes_examined = models.IntegerField(null=True, blank=True)
    lymph_nodes_positive = models.IntegerField(null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    surgery_source_value = models.CharField(max_length=50, null=True, blank=True)
    surgery_type_source_value = models.CharField(max_length=50, null=True, blank=True)
    surgical_margin_source_value = models.CharField(max_length=50, null=True, blank=True)
    residual_disease_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'cancer_surgery'

    def __str__(self):
        return f"Cancer Surgery {self.cancer_surgery_id} for {self.person}"


class CancerRadiation(models.Model):
    """
    CANCER_RADIATION table captures cancer-specific radiation therapy information including dose, fractionation, and target site.
    """
    cancer_radiation_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    cancer_diagnosis = models.ForeignKey(CancerDiagnosis, on_delete=models.CASCADE, null=True, blank=True)
    radiation_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='radiation_concept_id')
    radiation_start_date = models.DateField()
    radiation_start_datetime = models.DateTimeField(null=True, blank=True)
    radiation_end_date = models.DateField(null=True, blank=True)
    radiation_end_datetime = models.DateTimeField(null=True, blank=True)
    radiation_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='radiation_types', db_column='radiation_type_concept_id')
    radiation_site_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='radiation_sites', db_column='radiation_site_concept_id', null=True, blank=True)
    total_dose_gy = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fractions = models.IntegerField(null=True, blank=True)
    dose_per_fraction_gy = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    radiation_source_value = models.CharField(max_length=50, null=True, blank=True)
    radiation_type_source_value = models.CharField(max_length=50, null=True, blank=True)
    radiation_site_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'cancer_radiation'

    def __str__(self):
        return f"Cancer Radiation {self.cancer_radiation_id} for {self.person}"


class CancerBiomarker(models.Model):
    """
    CANCER_BIOMARKER table captures cancer-specific biomarker information including molecular markers, tumor markers, and genetic testing results.
    """
    cancer_biomarker_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    cancer_diagnosis = models.ForeignKey(CancerDiagnosis, on_delete=models.CASCADE, null=True, blank=True)
    biomarker_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='biomarker_concept_id')
    biomarker_date = models.DateField()
    biomarker_datetime = models.DateTimeField(null=True, blank=True)
    biomarker_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='biomarker_types', db_column='biomarker_type_concept_id')
    biomarker_result_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='biomarker_results', db_column='biomarker_result_concept_id', null=True, blank=True)
    biomarker_value_numeric = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    biomarker_value_text = models.CharField(max_length=255, null=True, blank=True)
    biomarker_unit_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='biomarker_units', db_column='biomarker_unit_concept_id', null=True, blank=True)
    test_method_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='test_methods', db_column='test_method_concept_id', null=True, blank=True)
    specimen_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='biomarker_specimen_types', db_column='specimen_type_concept_id', null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    biomarker_source_value = models.CharField(max_length=50, null=True, blank=True)
    biomarker_type_source_value = models.CharField(max_length=50, null=True, blank=True)
    biomarker_result_source_value = models.CharField(max_length=50, null=True, blank=True)
    biomarker_unit_source_value = models.CharField(max_length=50, null=True, blank=True)
    test_method_source_value = models.CharField(max_length=50, null=True, blank=True)
    specimen_type_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'cancer_biomarker'

    def __str__(self):
        return f"Cancer Biomarker {self.cancer_biomarker_id} for {self.person}"


class CancerResponse(models.Model):
    """
    CANCER_RESPONSE table captures cancer treatment response assessments including RECIST criteria and other response evaluation methods.
    """
    cancer_response_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    cancer_diagnosis = models.ForeignKey(CancerDiagnosis, on_delete=models.CASCADE, null=True, blank=True)
    cancer_treatment = models.ForeignKey(CancerTreatment, on_delete=models.CASCADE, null=True, blank=True)
    response_date = models.DateField()
    response_datetime = models.DateTimeField(null=True, blank=True)
    response_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='response_concept_id')
    response_method_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='response_methods', db_column='response_method_concept_id', null=True, blank=True)
    target_lesions_response_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='target_lesions_responses', db_column='target_lesions_response_concept_id', null=True, blank=True)
    non_target_lesions_response_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='non_target_lesions_responses', db_column='non_target_lesions_response_concept_id', null=True, blank=True)
    new_lesions_indicator = models.CharField(max_length=1, null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    response_source_value = models.CharField(max_length=50, null=True, blank=True)
    response_method_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'cancer_response'

    def __str__(self):
        return f"Cancer Response {self.cancer_response_id} for {self.person}"


class CancerMetastasis(models.Model):
    """
    CANCER_METASTASIS table captures information about metastatic sites and progression.
    """
    cancer_metastasis_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    cancer_diagnosis = models.ForeignKey(CancerDiagnosis, on_delete=models.CASCADE, null=True, blank=True)
    metastasis_date = models.DateField()
    metastasis_datetime = models.DateTimeField(null=True, blank=True)
    metastasis_site_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, db_column='metastasis_site_concept_id')
    metastasis_type_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='metastasis_types', db_column='metastasis_type_concept_id', null=True, blank=True)
    metastasis_status_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='metastasis_statuses', db_column='metastasis_status_concept_id', null=True, blank=True)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, null=True, blank=True)
    visit_detail = models.ForeignKey(VisitDetail, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    metastasis_site_source_value = models.CharField(max_length=50, null=True, blank=True)
    metastasis_type_source_value = models.CharField(max_length=50, null=True, blank=True)
    metastasis_status_source_value = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'cancer_metastasis'

    def __str__(self):
        return f"Cancer Metastasis {self.cancer_metastasis_id} for {self.person}"
